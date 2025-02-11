"""Functions to create an index of files for RAG."""
import logging
import os
import sys
from pathlib import Path

import chromadb
from dotenv import find_dotenv, load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from src.utilities.exceptions import MissingEnvironmentVariableError
from src.utilities.util_functions import join_paths
from src.utilities.llms import init_llms_mini


## Configure the logging level
logging.basicConfig(level=logging.INFO)

def relevant_extension(file_path: Path, file_extension_constraint: set[str]) -> bool:
    """Checker for whether file extension indicates a script."""
    # List of common code file extensions
    return file_path.suffix.lower() in file_extension_constraint


# read file content. place name of file in the top
def get_content(file_path: Path) -> str:
    """Collect file name and content to return them together as string."""
    with open(file_path, encoding="utf-8") as file:
        content = file.read()
    return file_path.name + "\n" + content


def files_in_directory(subfolders_with_files: list[str | Path],
                       work_dir: str,
                       file_extension_constraint: set[str] | None,
                       ) -> list[Path]:
    """
    Fetch relative paths of files in directory.
    TODO: resolve limited depth for traversing folders (only 2 levels at the time of writing)
    """
    files_to_describe = []
    for folder in subfolders_with_files:
        for root, _, files in os.walk(work_dir + str(folder)):
            for file in files:
                file_path = Path(root) / file
                if file_extension_constraint:
                    if relevant_extension(file_path, file_extension_constraint=file_extension_constraint):
                        files_to_describe.append(file_path)
                else:
                    files_to_describe.append(file_path)
    return files_to_describe


def save_file_description(file_path: Path, work_dir: str, description: str, description_folder: str) -> None:
    """Save file description."""
    file_name = file_path.relative_to(work_dir).as_posix().replace("/", "=")
    output_path = join_paths(description_folder, f"{file_name}.txt")
    with open(output_path, "w", encoding="utf-8") as out_file:
        out_file.write(description)


def output_descriptions(files_to_describe: list[Path], chain, description_folder: str, work_dir: str) -> None:
    """Generate & output file descriptions to designated directory in WORK_DIR."""
    # iterate over all files, take 8 files at once
    batch_size = 8
    for i in range(0, len(files_to_describe), batch_size):
        files_iteration = files_to_describe[i:i + batch_size]
        descriptions = chain.batch([get_content(file_path) for file_path in files_iteration])
        logging.debug(descriptions)
        [save_file_description(file_path=file_path,
                               work_dir=work_dir,
                               description=description,
                               description_folder=description_folder,
                               ) for file_path,
                               description in zip(files_iteration, descriptions, strict=True)]


def produce_descriptions(subfolders_with_files: list[str | Path],
                       file_description_dir: str,
                       work_dir: str,
                       file_extension_constraint: set[str] | None,
                       ) -> None:
    """Produce short descriptions of files. Store them in .clean_coder folder in WORK_DIR."""
    files_to_describe = files_in_directory(subfolders_with_files=subfolders_with_files, work_dir=work_dir, file_extension_constraint=file_extension_constraint)

    prompt = ChatPromptTemplate.from_template(
    """Describe the following code in 4 sentences or less, focusing only on important information from integration point of view.
    Write what file is responsible for.\n\n'''\n{code}'''
    """,
    )

    llms = init_llms_mini(tools=[], run_name="File Describer")
    llm = llms[0]
    chain = prompt | llm | StrOutputParser()
    description_folder = join_paths(work_dir, file_description_dir)
    Path(description_folder).mkdir(parents=True, exist_ok=True)
    output_descriptions(files_to_describe=files_to_describe, work_dir=work_dir, chain=chain, description_folder=description_folder)


def read_file_descriptions_and_upload_to_base(collection: chromadb.PersistentClient, work_dir: str, file_description_dir: str) -> None:
    """Insert file information to chroma database."""
    description_folder = join_paths(work_dir, file_description_dir)
    for root, _, files in os.walk(description_folder):
        for file in files:
            file_path = Path(root) / file
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            collection.upsert(
                documents=[
                    content,
                ],
                ids=[file_path.name.replace("=", "/").removesuffix(".txt")],
            )

def upload_descriptions_to_vdb(chroma_collection_name: str, work_dir: str, file_description_dir: str, vdb_location: str = ".clean_coder/chroma_base") -> None:
    """Upload file descriptions to chroma database."""
    chroma_client = chromadb.PersistentClient(path=join_paths(work_dir, vdb_location))
    collection = chroma_client.get_or_create_collection(
        name=chroma_collection_name,
    )

    # read files and upload to base
    read_file_descriptions_and_upload_to_base(collection=collection, work_dir=work_dir, file_description_dir=file_description_dir)


if __name__ == "__main__":
    #provide optionally which subfolders needs to be checked, if you don't want to describe all project folder
    # load environment
    load_dotenv(find_dotenv())
    work_dir = os.getenv("WORK_DIR")
    if not work_dir:
        msg = "WORK_DIR variable not provided. Please add WORK_DIR to .env file"
        raise MissingEnvironmentVariableError(msg)
    file_description_dir = ".clean_coder/workdir_file_and_folder_descriptions"
    file_extension_constraint =     code_extensions = {
        ".js", ".jsx", ".ts", ".tsx", ".vue", ".py", ".rb", ".php", ".java", ".c", ".cpp", ".cs", ".go", ".swift",
        ".kt", ".rs", ".htm",".html", ".css", ".scss", ".sass", ".less", ".prompt",
    }
    produce_descriptions(subfolders_with_files=["/"],
                       file_description_dir=file_description_dir,
                       work_dir=work_dir,
                       file_extension_constraint=file_extension_constraint,
                       )
    chroma_collection_name = f"clean_coder_{Path(work_dir).name}_file_descriptions"
    upload_descriptions_to_vdb(chroma_collection_name=chroma_collection_name, work_dir=work_dir, file_description_dir=file_description_dir)
