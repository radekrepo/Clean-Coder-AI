import os
from pathlib import Path
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic
import chromadb
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
work_dir = os.getenv("WORK_DIR")


def is_code_file(file_path):
    # List of common code file extensions
    code_extensions = {
        '.js', '.jsx', '.ts', '.tsx', '.vue', '.py', '.rb', '.php', '.java', '.c', '.cpp', '.cs', '.go', '.swift',
        '.kt', '.rs', '.htm','.html', '.css', '.scss', '.sass', '.less'
    }
    return file_path.suffix.lower() in code_extensions


# read file content. place name of file in the top
def get_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    content = file_path.name + '\n' + content
    return content


def write_descriptions(subfolders_with_files=['/']):
    all_files = []

    for folder in subfolders_with_files:
        for root, _, files in os.walk(work_dir + folder):
            for file in files:
                file_path = Path(root) / file
                if is_code_file(file_path):
                    all_files.append(file_path)

    prompt = ChatPromptTemplate.from_template(
"""Describe the following code in 4 sentences or less, focusing only on important information from integration point of view.
Write what file is responsible for.\n\n'''\n{code}'''
"""
    )
    llm = ChatAnthropic(model='claude-3-5-sonnet-20240620')
    chain = prompt | llm | StrOutputParser()

    # iterate over all files, take 8 files at once
    batch_size = 8
    for i in range(0, len(all_files), batch_size):
        files_iteration = all_files[i:i + batch_size]
        descriptions = chain.batch([get_content(file_path) for file_path in files_iteration])
        print(descriptions)

        for file_path, description in zip(files_iteration, descriptions):
            file_name = file_path.relative_to(work_dir).as_posix().replace('/', '=')
            output_path = Path(work_dir + '.clean_coder/files_and_folders_descriptions') / f"{file_name}.txt"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(description)


def upload_descriptions_to_vdb():
    chroma_client = chromadb.PersistentClient(path=os.getenv('WORK_DIR') + '.clean_coder/chroma_base')
    collection_name = f"clean_coder_{Path(work_dir).name}_file_descriptions"

    collection = chroma_client.get_or_create_collection(
        name=collection_name
    )

    # read files and upload to base
    for root, _, files in os.walk(work_dir + '.clean_coder/files_and_folders_descriptions'):
        for file in files:
            file_path = Path(root) / file
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            collection.upsert(
                documents=[
                    content
                ],
                ids=[file_path.name.replace('=', '/').removesuffix(".txt")],
            )


if __name__ == '__main__':
    #provide optionally which subfolders needs to be checked, if you don't want to describe all project folder
    write_descriptions(subfolders_with_files=['/'])

    upload_descriptions_to_vdb()
