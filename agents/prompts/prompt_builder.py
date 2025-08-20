import logging
import textwrap

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class PromptBuilder:
    """Basic prompt building engine for LLM chatbots"""
    def __init__(self):
        self.components = []
        self.section_headers = []


    def add_text(self, text: str):
        """Adds text to the prompt components"""
        self.components.append(self._clean(text))


    def add_section(self, title: str, content: str):
        """Adds a new section and it's content to the prompt components"""
        self.section_headers.append(title)
        section = f"### {title}\n{self._clean(content)}"
        self.components.append(section)


    def add_dataframe_summary(self, df, title=None, max_rows=5, max_cols=5):
        """Adds a summary of a dataframe in a printed format, not great for compression"""
        summary = df.iloc[:max_rows, :max_cols].to_markdown(index=False)
        if title:
            self.add_section(title, summary)
        else:
            self.components.append(summary)


    def add_dict_summary(self, data: dict, title=None):
        """Turns a dictionary into a nice summary without curly brackets"""
        summary = '\n'.join(f"{k}: {v}" for k, v in data.items())
        if title:
            self.add_section(title, summary)
        else:
            self.components.append(summary)


    def add_comparison(self, item_a, item_b, label_a="A", label_b="B"):
        """Adds a labeled comparison to the prompt"""
        comparison = f"{label_a}: {item_a}\n{label_b}: {item_b}"
        self.add_section("Comparison", comparison)


    def build(self, separator="\n\n"):
        return separator.join(self.components)


    def _clean(self, text: str):
        return textwrap.dedent(text).strip()
    

    @property
    def prompt(self):
        return self.build()


    def __repr__(self):
        return f"{self.__class__.__name__}(prompt_attrs={len(self.components)})"
    


if __name__ == "__main__":
    import pandas as pd

    test_prompt = PromptBuilder("Test PromptBuilder")

    test_prompt.add_text("Hello chat")
    logger.info(f"Test for BasePrompt method add_text, componenst: {test_prompt.components}")
    logger.info(f"Test for BasePrompt method add_text, repr: {test_prompt}")
    logger.info(f"Test for BasePrompt method add_text, .prompt: {test_prompt.prompt}")

    test_prompt.add_section("Creativity", "You are playing the role of a creative director who has some difficult business decisions coming up")
    logger.info(f"Test for BasePrompt method add_section, componenst: {test_prompt.components}")
    logger.info(f"Test for BasePrompt method add_section, .prompt: {test_prompt.prompt}")

    df_dict = {
        f"col_{i}": [f"R{j}_C{i}" for j in range(20)]
        for i in range(20)
    }
    df = pd.DataFrame.from_dict(df_dict)
    
    test_prompt.add_dataframe_summary(df, title="Boofy Datafeame")
    logger.info(f"Test for BasePrompt method add_dataframe_summary, componenst: {test_prompt.components}")
    logger.info(f"Test for BasePrompt method add_dataframe_summary, .prompt: {test_prompt.prompt}")

    dictionary = {
        "A" : "Apple",
        "B" : "Basketball",
        "C" : "Clinton",
        "D" : "Dynamite"
    }

    test_prompt.add_dict_summary(dictionary, title="Alphabet Soup")
    logger.info(f"Test for BasePrompt method add_dict_summary, componenst: {test_prompt.components}")
    logger.info(f"Test for BasePrompt method add_dict_summary, .prompt: {test_prompt.prompt}")

    test_prompt.add_comparison("apples", "oranges")
    logger.info(f"Test for BasePrompt method add_comparison, componenst: {test_prompt.components}")
    logger.info(f"Test for BasePrompt method add_comparison, .prompt: {test_prompt.prompt}")

