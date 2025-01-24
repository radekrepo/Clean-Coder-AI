<div align="center">
  <img
    src="/assets/starting_video.gif"
    alt="Starting video"
  >
  <br>
  <img src="/assets/logo_wide_2.png" alt="Logo">
  <h2>Tired of explaining AI what to do? Let Clean Coder handle it for you.</h2>
  <br>
  Clean Coder is your 2-in-1 AI Scrum Master and Developer. Delegate planning, managing, and coding to AI. Agents create tasks within Todoist, write code, and test it, helping you create great projects with minimal effort and stress!
  <br>
  <br>
  <h3>⭐️ Your star motivates me to introduce new cool features! ⭐️</h3>  
  <br>

[![Docs](https://img.shields.io/badge/docs-latest-blue)](https://clean-coder.dev)
[![Discord](https://img.shields.io/static/v1?logo=discord&label=discord&message=Join&color=brightgreen)](https://discord.gg/8gat7Pv7QJ)

  <img src="/assets/CC_diagram_full.png" alt="Logo">
</div>

## 🏖️ Relax and watch it code

```
git clone https://github.com/GregorD1A1/Clean-Coder-AI
cd Clean-Coder-AI

pip install -r requirements.txt

python single_task_coder.py
```
or (recommended) check detailed instructions [how to start in documentation](https://clean-coder.dev/quick_start/programmer_pipeline/).

You can also [deploy with Docker](https://clean-coder.dev/quick_start/run_with_docker/).


## 📺 Demo videos

Create an entire web app ~~with~~ by Clean Coder:

<div align="center">
<a href="https://youtu.be/aNpB-Tw-YPw" title="Greg's Tech video">
  <img src="https://img.youtube.com/vi/aNpB-Tw-YPw/maxresdefault.jpg" width="600" alt="Demo video">
</a>
</div>


## ✨ Key advantages:

- Get project supervised by [Manager agent](https://clean-coder.dev/quick_start/manager/) with thoroughly-described tasks organized in Todoist, just like with a human scrum master.
- Watch tasks executed one by one by [Programming agents](https://clean-coder.dev/quick_start/programmer_pipeline/), with a well-designed context pipeline and advanced techniques for enhanced intelligence.
- Allow AI to see frontend it creates with [frontend feedback feature](https://clean-coder.dev/features/frontend_feedback/). At the day of writing no other AI coder has that feature.
- Create a [frontend based on images](https://clean-coder.dev/features/working_with_images/) with designs.
- [Speak to Clean Coder](https://clean-coder.dev/features/talk_to_cc/) instead of writing.
- Automatic file linting prevents from introducing incorrect changes and [log check for self-debug](https://clean-coder.dev/advanced_features_installation/logs_check/).
- File Researcher agent with (but not only) [RAG tool](https://clean-coder.dev/advanced_features_installation/similarity_search_for_researcher/) for effective searching of project files.
- [Sensitive files protection](https://clean-coder.dev/features/sensitive_file_protection/) from being watched by AI.


## ⛓️‍💥 Something got broken?

Report bugs or propose new features for Clean Coder on our [Discord](https://discord.gg/8gat7Pv7QJ)!

## 🎖️ Hall of Fame
<br>
<div align="center">
  <a href="https://github.com/Grigorij-Dudnik/Clean-Coder-AI/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=Grigorij-Dudnik/Clean-Coder-AI&1" />
  </a>
</div>
<br>

Sweat, tears and endless glory... [Join the Clean Coder contributors](https://clean-coder.dev/community/contributions_guide/)!


TODO for this branch:
There are a few notable repositories and tools for automated unit test generation in Python besides Pynguin (https://github.com/se2p/pynguin):

Auger: Auger is an automated unit test generation tool for Python[3]. It can generate unit tests by observing the runtime behavior of your code. Key features include:

Supports both Python 2 and 3
Can generate tests for classes and modules
Automatically mocks external dependencies
Generates readable and maintainable test code
CodiumAI: While not an open-source repository, CodiumAI is a platform that offers automated unit test generation for Python[5]. It integrates with popular IDEs like VS Code and provides:

Quick test generation for Python classes and functions
Code analysis to understand the purpose of the code
Ability to customize and exclude specific tests
Hypothesis: Although not strictly a test generator, Hypothesis is a powerful property-based testing library for Python that can automatically generate test cases based on specified properties and constraints.

MutPy: While not generating unit tests directly, MutPy is a mutation testing tool for Python that can help identify weaknesses in existing test suites, indirectly assisting in improving test coverage.

pytest-randomly: This pytest plugin doesn't generate tests but helps in making existing tests more robust by randomizing their execution order, potentially uncovering hidden dependencies between tests.

While these tools offer various approaches to automated testing in Python, Pynguin stands out as a comprehensive framework specifically designed for automated unit test generation[1][2][4]. It offers features like:

Support for different test generation techniques
Extensibility for researchers to implement new approaches
Integration with popular Python testing frameworks
Ability to generate high-coverage regression tests
Each of these tools has its strengths and may be suitable for different use cases or development workflows. Developers should evaluate them based on their specific needs and project requirements.
