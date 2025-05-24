import logging
import re
from typing import Any, Dict

from .reasoning_patterns import ReasoningPatternLibrary

logger = logging.getLogger(__name__)


class TaskPattern:
    """Base class for task-specific patterns."""

    def __init__(self, name: str, description: str):
        """
        Initialize the task pattern.

        Args:
            name: Name of the task pattern
            description: Description of the task pattern
        """
        self.name = name
        self.description = description
        self.reasoning_library = ReasoningPatternLibrary()

    def generate_system_prompt(self, **kwargs) -> str:
        """
        Generate a system prompt for this task pattern.

        Args:
            **kwargs: Additional parameters for prompt generation

        Returns:
            System prompt
        """
        raise NotImplementedError("Subclasses must implement generate_system_prompt")

    def generate_task_prompt(self, task: str, **kwargs) -> str:
        """
        Generate a task prompt for this task pattern.

        Args:
            task: Original task description
            **kwargs: Additional parameters for prompt generation

        Returns:
            Task prompt
        """
        raise NotImplementedError("Subclasses must implement generate_task_prompt")

    def process_result(self, result: str) -> Dict[str, Any]:
        """
        Process the result from the agent for this task pattern.

        Args:
            result: Result string from agent

        Returns:
            Processed result
        """
        raise NotImplementedError("Subclasses must implement process_result")


class CodeGenerationPattern(TaskPattern):
    """
    Pattern for code generation tasks.
    Specialized for producing high-quality, well-documented code.
    """

    def __init__(self):
        """Initialize the Code Generation pattern."""
        super().__init__(
            name="Code Generation",
            description="Generate high-quality, well-documented code from requirements",
        )

    def generate_system_prompt(self, **kwargs) -> str:
        """Generate a system prompt for code generation."""
        language = kwargs.get("language", "python")
        complexity = kwargs.get("complexity", "medium")
        style = kwargs.get("style", "standard")

        # Define base prompt
        prompt = (
            "You are an expert software developer specializing in writing high-quality, maintainable code. "
            "Your code should be well-structured, properly documented, and follow best practices for the language. "
            "Include appropriate error handling, input validation, and consideration of edge cases. "
            "Provide brief explanations of key design decisions or non-obvious implementations."
        )

        # Add language-specific guidance
        if language.lower() == "python":
            prompt += (
                "\n\nFor Python code:"
                "\n- Follow PEP 8 style guidelines"
                "\n- Use meaningful variable and function names"
                "\n- Include docstrings with type annotations"
                "\n- Use appropriate data structures for the task"
                "\n- Include helpful comments where needed without being excessive"
            )
            if style == "functional":
                prompt += "\n- Prefer functional programming patterns where appropriate"
            elif style == "oop":
                prompt += (
                    "\n- Prefer object-oriented programming patterns where appropriate"
                )

        elif language.lower() in ["javascript", "typescript"]:
            prompt += (
                f"\n\nFor {language} code:"
                "\n- Follow established style conventions (e.g., Airbnb style guide)"
                "\n- Use ES6+ features appropriately"
                "\n- Include JSDoc comments for functions and classes"
                "\n- Use meaningful variable and function names"
            )
            ts_type_note = (
                "\n- Include TypeScript type annotations"
                if language.lower() == "typescript"
                else ""
            )
            prompt += ts_type_note
            if style == "functional":
                prompt += "\n- Prefer functional programming patterns where appropriate"
            elif style == "oop":
                prompt += (
                    "\n- Prefer object-oriented programming patterns where appropriate"
                )

        # Add complexity guidance
        if complexity == "high":
            prompt += (
                "\n\nThis is a complex task that may require:"
                "\n- Careful algorithm design and optimization"
                "\n- Modular design with clear separation of concerns"
                "\n- Comprehensive error handling"
                "\n- Consideration of performance implications"
            )
        elif complexity == "low":
            prompt += (
                "\n\nThis is a straightforward task. Focus on:"
                "\n- Clear, readable code over excessive optimization"
                "\n- Practical documentation and error handling"
                "\n- Simple implementation that directly solves the problem"
            )

        # Add reasoning pattern integration
        reasoning_pattern = kwargs.get("reasoning_pattern", "chain_of_thought")
        if reasoning_pattern:
            pattern = self.reasoning_library.get_pattern(reasoning_pattern)
            if pattern:
                reasoning_prompt = pattern.generate_system_prompt(domain="code")
                prompt += f"\n\n{reasoning_prompt}"

        return prompt

    def generate_task_prompt(self, task: str, **kwargs) -> str:
        """Generate a task prompt for code generation."""
        language = kwargs.get("language", "python")
        include_tests = kwargs.get("include_tests", True)
        include_examples = kwargs.get("include_examples", True)
        reasoning_pattern = kwargs.get("reasoning_pattern", "chain_of_thought")

        # Build task prompt
        prompt = (
            f"Please write {language} code for the following requirement:\n\n{task}\n\n"
        )

        if include_examples:
            prompt += "Include example usage showing how your code would be used.\n\n"

        if include_tests:
            prompt += f"Include appropriate tests for your {language} code.\n\n"

        # Add reasoning pattern
        if reasoning_pattern:
            pattern = self.reasoning_library.get_pattern(reasoning_pattern)
            if pattern:
                reasoning_prompt = pattern.generate_task_prompt(
                    "Think about the design and implementation of this code",
                    domain="code",
                )
                prompt += f"{reasoning_prompt}\n\n"

        prompt += (
            "Your response should include:\n"
            "1. The complete, executable code\n"
            "2. Brief explanation of design decisions\n"
            f"3. {'Tests and ' if include_tests else ''}Example usage"
        )

        return prompt

    def process_result(self, result: str) -> Dict[str, Any]:
        """Process code generation result."""
        # Extract code blocks
        code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", result, re.DOTALL)

        # Extract explanation parts (text outside code blocks)
        explanation_parts = re.split(r"```(?:\w+)?\n.*?```", result, flags=re.DOTALL)
        explanation_parts = [part.strip() for part in explanation_parts if part.strip()]

        # Join explanations
        explanation = "\n\n".join(explanation_parts)

        # Try to separate implementation and tests
        implementation = ""
        tests = ""
        examples = ""

        if code_blocks:
            # Assume first block is implementation if multiple blocks
            implementation = code_blocks[0]

            # Look for test code in subsequent blocks or in the same block
            for block in code_blocks[1:]:
                if re.search(r"(?:test|assert|unittest|pytest)", block, re.IGNORECASE):
                    tests = block
                elif re.search(r"example|usage|demo", block, re.IGNORECASE):
                    examples = block

            # If no tests found in separate blocks, check if tests are in the implementation
            if not tests and len(code_blocks) == 1:
                test_section = re.search(
                    r"(?:class|def)\s+\w*[Tt]est\w*.*?(?:$|(?=class|def))",
                    implementation,
                    re.DOTALL,
                )
                if test_section:
                    tests = test_section.group(0)

        return {
            "task_pattern": "code_generation",
            "implementation": implementation,
            "tests": tests,
            "examples": examples,
            "explanation": explanation,
            "full_response": result,
        }


class DataAnalysisPattern(TaskPattern):
    """
    Pattern for data analysis tasks.
    Specialized for data exploration, visualization, and insights.
    """

    def __init__(self):
        """Initialize the Data Analysis pattern."""
        super().__init__(
            name="Data Analysis",
            description="Analyze data to extract insights and visualizations",
        )

    def generate_system_prompt(self, **kwargs) -> str:
        """Generate a system prompt for data analysis."""
        domain = kwargs.get("domain", "general")
        analysis_depth = kwargs.get("analysis_depth", "medium")
        include_code = kwargs.get("include_code", True)

        # Define base prompt
        prompt = (
            "You are an expert data analyst specialized in extracting meaningful insights from data. "
            "Your analysis should be thorough, methodical, and focused on addressing the key questions. "
            "Consider statistical significance, potential biases, and limitations in the data. "
            "Present your findings clearly with appropriate visualizations and interpretations."
        )

        # Add domain-specific guidance
        if domain == "business":
            prompt += (
                "\n\nFor business data analysis:"
                "\n- Focus on actionable insights that can drive decision-making"
                "\n- Consider financial implications, market trends, and competitive factors"
                "\n- Connect analysis to key business metrics and KPIs"
                "\n- Highlight opportunities for optimization or growth"
            )
        elif domain == "scientific":
            prompt += (
                "\n\nFor scientific data analysis:"
                "\n- Apply rigorous statistical methods appropriate for the data"
                "\n- Consider experimental design and potential confounding factors"
                "\n- Be precise about statistical significance and confidence intervals"
                "\n- Connect findings to the broader scientific literature"
            )

        # Add analysis depth guidance
        if analysis_depth == "exploratory":
            prompt += (
                "\n\nProvide exploratory data analysis:"
                "\n- Data profiling and quality assessment"
                "\n- Distribution analysis and descriptive statistics"
                "\n- Identification of patterns, trends, and outliers"
                "\n- Initial hypotheses for further investigation"
            )
        elif analysis_depth == "comprehensive":
            prompt += (
                "\n\nProvide comprehensive data analysis:"
                "\n- Thorough exploration of data distributions and relationships"
                "\n- Statistical testing of key hypotheses"
                "\n- Advanced modeling or clustering as appropriate"
                "\n- Detailed interpretation of findings with practical implications"
            )

        # Add code guidance if needed
        if include_code:
            prompt += (
                "\n\nInclude Python code for your analysis:"
                "\n- Use pandas for data manipulation"
                "\n- Use matplotlib/seaborn/plotly for visualizations"
                "\n- Include clear code comments"
                "\n- Focus on reproducible, efficient code"
            )

        # Add reasoning pattern integration
        reasoning_pattern = kwargs.get("reasoning_pattern", "scientific_method")
        if reasoning_pattern:
            pattern = self.reasoning_library.get_pattern(reasoning_pattern)
            if pattern:
                reasoning_prompt = pattern.generate_system_prompt(
                    domain="data_analysis"
                )
                prompt += f"\n\n{reasoning_prompt}"

        return prompt

    def generate_task_prompt(self, task: str, **kwargs) -> str:
        """Generate a task prompt for data analysis."""
        include_code = kwargs.get("include_code", True)
        data_description = kwargs.get("data_description", "")
        key_questions = kwargs.get("key_questions", [])
        reasoning_pattern = kwargs.get("reasoning_pattern", "scientific_method")

        # Build task prompt
        prompt = f"Please perform data analysis for the following task:\n\n{task}\n\n"

        if data_description:
            prompt += f"Data description:\n{data_description}\n\n"

        if key_questions:
            prompt += "Key questions to address:\n"
            for i, question in enumerate(key_questions, 1):
                prompt += f"{i}. {question}\n"
            prompt += "\n"

        # Add reasoning pattern
        if reasoning_pattern:
            pattern = self.reasoning_library.get_pattern(reasoning_pattern)
            if pattern:
                reasoning_prompt = pattern.generate_task_prompt(
                    "Approach this data analysis systematically", domain="data_analysis"
                )
                prompt += f"{reasoning_prompt}\n\n"

        prompt += (
            "Your response should include:\n"
            "1. Data exploration and cleaning approach\n"
            "2. Key findings and insights\n"
            "3. Appropriate visualizations\n"
            "4. Limitations and potential biases\n"
            "5. Recommendations based on the analysis\n"
        )

        if include_code:
            prompt += "6. Python code used for the analysis\n"

        return prompt

    def process_result(self, result: str) -> Dict[str, Any]:
        """Process data analysis result."""
        # Extract code blocks
        code_blocks = re.findall(r"```(?:python)?\n(.*?)```", result, re.DOTALL)

        # Extract sections from the text
        sections = {}

        # Look for data exploration section
        exploration_match = re.search(
            r"(?:^|\n)(?:Data Exploration|Exploratory Analysis|Data Cleaning)(?::|:.*?)?\n(.*?)(?=(?:\n##|\n#|\n\d\.|\Z))",
            result,
            re.IGNORECASE | re.DOTALL,
        )
        if exploration_match:
            sections["data_exploration"] = exploration_match.group(1).strip()

        # Look for findings/insights section
        findings_match = re.search(
            r"(?:^|\n)(?:Key Findings|Insights|Analysis Results)(?::|:.*?)?\n(.*?)(?=(?:\n##|\n#|\n\d\.|\Z))",
            result,
            re.IGNORECASE | re.DOTALL,
        )
        if findings_match:
            sections["key_findings"] = findings_match.group(1).strip()

        # Look for limitations section
        limitations_match = re.search(
            r"(?:^|\n)(?:Limitations|Biases|Caveats)(?::|:.*?)?\n(.*?)(?=(?:\n##|\n#|\n\d\.|\Z))",
            result,
            re.IGNORECASE | re.DOTALL,
        )
        if limitations_match:
            sections["limitations"] = limitations_match.group(1).strip()

        # Look for recommendations section
        recommendations_match = re.search(
            r"(?:^|\n)(?:Recommendations|Suggestions|Next Steps)(?::|:.*?)?\n(.*?)(?=(?:\n##|\n#|\n\d\.|\Z))",
            result,
            re.IGNORECASE | re.DOTALL,
        )
        if recommendations_match:
            sections["recommendations"] = recommendations_match.group(1).strip()

        return {
            "task_pattern": "data_analysis",
            "sections": sections,
            "code": "\n\n".join(code_blocks) if code_blocks else "",
            "full_response": result,
        }


class ContentCreationPattern(TaskPattern):
    """
    Pattern for content creation tasks.
    Specialized for generating engaging, well-structured content.
    """

    def __init__(self):
        """Initialize the Content Creation pattern."""
        super().__init__(
            name="Content Creation",
            description="Generate engaging, well-structured content",
        )

    def generate_system_prompt(self, **kwargs) -> str:
        """Generate a system prompt for content creation."""
        content_type = kwargs.get("content_type", "article")
        audience = kwargs.get("audience", "general")
        tone = kwargs.get("tone", "informative")

        # Define base prompt
        prompt = (
            "You are an expert content creator specialized in producing high-quality, engaging content. "
            "Your writing should be clear, well-structured, and tailored to the target audience. "
            "Focus on delivering value through insightful content that resonates with readers."
        )

        # Add content type guidance
        if content_type == "article":
            prompt += (
                "\n\nFor article creation:"
                "\n- Craft a compelling headline that drives interest"
                "\n- Begin with a strong hook to capture attention"
                "\n- Organize content with clear headings and subheadings"
                "\n- Include relevant examples, data, or quotes to support points"
                "\n- End with a satisfying conclusion and, if appropriate, a call to action"
            )
        elif content_type == "blog_post":
            prompt += (
                "\n\nFor blog post creation:"
                "\n- Use a conversational, approachable style"
                "\n- Include a compelling introduction that establishes relevance"
                "\n- Break content into scannable sections with descriptive headings"
                "\n- Incorporate personal insights or stories where appropriate"
                "\n- End with discussion questions or next steps"
            )
        elif content_type == "social_media":
            prompt += (
                "\n\nFor social media content:"
                "\n- Create concise, impactful messages that spark engagement"
                "\n- Optimize for the specific platform's format and audience"
                "\n- Include attention-grabbing elements in the first line"
                "\n- Consider adding relevant hashtags or calls to action"
                "\n- Craft content that encourages sharing or discussion"
            )

        # Add audience guidance
        if audience == "technical":
            prompt += (
                "\n\nFor a technical audience:"
                "\n- Use appropriate technical terminology and concepts"
                "\n- Provide sufficient depth on complex topics"
                "\n- Include relevant technical details and examples"
                "\n- Assume background knowledge while still making content accessible"
            )
        elif audience == "beginner":
            prompt += (
                "\n\nFor a beginner audience:"
                "\n- Explain concepts clearly without assuming prior knowledge"
                "\n- Define technical terms when first introduced"
                "\n- Use analogies and examples to illustrate complex ideas"
                "\n- Focus on building a solid foundation of understanding"
            )
        elif audience == "business":
            prompt += (
                "\n\nFor a business audience:"
                "\n- Focus on practical applications and business value"
                "\n- Include relevant metrics, ROI considerations, or case studies"
                "\n- Be concise and respectful of readers' limited time"
                "\n- Frame information in terms of business outcomes and benefits"
            )

        # Add tone guidance
        if tone == "professional":
            prompt += (
                "\n\nMaintain a professional tone:"
                "\n- Use clear, precise language"
                "\n- Avoid colloquialisms, slang, or overly casual expressions"
                "\n- Present balanced perspectives backed by evidence"
                "\n- Maintain an authoritative but not condescending voice"
            )
        elif tone == "conversational":
            prompt += (
                "\n\nMaintain a conversational tone:"
                "\n- Write as if speaking directly to the reader"
                "\n- Use contractions, questions, and a more relaxed style"
                "\n- Include occasional humor or personality where appropriate"
                "\n- Create a sense of connection with the reader"
            )
        elif tone == "persuasive":
            prompt += (
                "\n\nMaintain a persuasive tone:"
                "\n- Present compelling arguments supported by evidence"
                "\n- Address potential counterarguments respectfully"
                "\n- Use rhetorical techniques effectively"
                "\n- Guide the reader toward a specific viewpoint or action"
            )

        # Add reasoning pattern integration
        reasoning_pattern = kwargs.get("reasoning_pattern", "self_reflection")
        if reasoning_pattern:
            pattern = self.reasoning_library.get_pattern(reasoning_pattern)
            if pattern:
                reasoning_prompt = pattern.generate_system_prompt(domain="writing")
                prompt += f"\n\n{reasoning_prompt}"

        return prompt

    def generate_task_prompt(self, task: str, **kwargs) -> str:
        """Generate a task prompt for content creation."""
        content_type = kwargs.get("content_type", "article")
        word_count = kwargs.get("word_count", "600-800")
        key_points = kwargs.get("key_points", [])
        reasoning_pattern = kwargs.get("reasoning_pattern", "self_reflection")

        # Build task prompt
        prompt = (
            f"Please create {content_type} content for the following:\n\n{task}\n\n"
        )

        prompt += f"Target word count: {word_count} words\n\n"

        if key_points:
            prompt += "Key points to include:\n"
            for i, point in enumerate(key_points, 1):
                prompt += f"{i}. {point}\n"
            prompt += "\n"

        # Add reasoning pattern
        if reasoning_pattern:
            pattern = self.reasoning_library.get_pattern(reasoning_pattern)
            if pattern:
                reasoning_prompt = pattern.generate_task_prompt(
                    f"Create {content_type} content for this topic", domain="writing"
                )
                prompt += f"{reasoning_prompt}\n\n"

        prompt += (
            "Your response should include:\n"
            f"1. An engaging {'headline' if content_type == 'article' else 'title'}\n"
            "2. Well-structured content with appropriate headings\n"
            "3. Engaging opening and satisfying conclusion\n"
            "4. Content that addresses all the key points requested\n"
        )

        return prompt

    def process_result(self, result: str) -> Dict[str, Any]:
        """Process content creation result."""
        # Extract title/headline
        title = ""
        title_match = re.search(r"^#\s*(.*?)$", result, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            # Try alternative formats
            alt_title_match = re.search(
                r"(?:Title:|Headline:)\s*(.*?)$", result, re.MULTILINE
            )
            if alt_title_match:
                title = alt_title_match.group(1).strip()
            else:
                # Just use the first line
                first_line = result.split("\n")[0]
                if len(first_line) < 100:  # Reasonable title length
                    title = first_line.strip()

        # Extract sections (assume h2 headings are section breaks)
        sections = []
        section_matches = re.findall(
            r"##\s*(.*?)$\s*(.*?)(?=\n##|\Z)", result, re.MULTILINE | re.DOTALL
        )

        if section_matches:
            for heading, content in section_matches:
                sections.append(
                    {"heading": heading.strip(), "content": content.strip()}
                )

        # If no sections found, try to identify content structure another way
        if not sections:
            # Try to split by subheadings in alternative formats
            section_matches = re.findall(
                r"(?:^|\n)(?:\*\*|__)([^*_]+)(?:\*\*|__)(?:\s*:?\s*)(.*?)(?=\n(?:\*\*|__)[^*_]+(?:\*\*|__)|$)",
                result,
                re.DOTALL,
            )

            if section_matches:
                for heading, content in section_matches:
                    sections.append(
                        {"heading": heading.strip(), "content": content.strip()}
                    )

        # Extract introduction and conclusion
        introduction = ""
        conclusion = ""

        # Introduction is content before first section heading
        intro_match = re.search(r"^(.*?)(?=\n##|\n\*\*|\n__)", result, re.DOTALL)
        if intro_match:
            intro_text = intro_match.group(1).strip()
            if title and intro_text.startswith(title):
                intro_text = intro_text[len(title) :].strip()
            introduction = intro_text

        # Conclusion might be in a section with a conclusion-like heading
        conclusion_sections = [
            s
            for s in sections
            if any(
                keyword in s["heading"].lower()
                for keyword in ["conclusion", "summary", "final", "closing"]
            )
        ]
        if conclusion_sections:
            conclusion = conclusion_sections[0]["content"]
        else:
            # If no conclusion section, use the last section
            if sections:
                conclusion = sections[-1]["content"]

        # Calculate word count
        word_count = len(re.findall(r"\b\w+\b", result))

        return {
            "task_pattern": "content_creation",
            "title": title,
            "introduction": introduction,
            "sections": sections,
            "conclusion": conclusion,
            "word_count": word_count,
            "full_content": result,
        }


class DecisionSupportPattern(TaskPattern):
    """
    Pattern for decision support tasks.
    Specialized for analyzing options and making recommendations.
    """

    def __init__(self):
        """Initialize the Decision Support pattern."""
        super().__init__(
            name="Decision Support",
            description="Analyze options and provide decision recommendations",
        )

    def generate_system_prompt(self, **kwargs) -> str:
        """Generate a system prompt for decision support."""
        decision_type = kwargs.get("decision_type", "general")
        criteria_focus = kwargs.get("criteria_focus", "balanced")
        formality = kwargs.get("formality", "medium")

        # Define base prompt
        prompt = (
            "You are an expert analyst specializing in decision support. "
            "Your role is to provide balanced, thorough analysis of options to support informed decision-making. "
            "Consider multiple perspectives, weigh trade-offs carefully, and provide clear recommendations "
            "while acknowledging uncertainties and limitations."
        )

        # Add decision type guidance
        if decision_type == "technical":
            prompt += (
                "\n\nFor technical decisions:"
                "\n- Evaluate technical feasibility, scalability, and maintainability"
                "\n- Consider implementation complexity and technical debt"
                "\n- Assess alignment with existing technical infrastructure"
                "\n- Analyze technical risks and mitigation strategies"
            )
        elif decision_type == "strategic":
            prompt += (
                "\n\nFor strategic decisions:"
                "\n- Consider long-term implications and alignment with goals"
                "\n- Evaluate market conditions and competitive dynamics"
                "\n- Assess resource requirements and organizational capacity"
                "\n- Identify strategic risks and potential contingency plans"
            )
        elif decision_type == "resource_allocation":
            prompt += (
                "\n\nFor resource allocation decisions:"
                "\n- Analyze ROI and opportunity costs for different allocations"
                "\n- Consider short-term needs versus long-term investments"
                "\n- Evaluate resource constraints and optimization opportunities"
                "\n- Assess risks of under-investment in critical areas"
            )

        # Add criteria focus guidance
        if criteria_focus == "quantitative":
            prompt += (
                "\n\nFocus on quantitative criteria:"
                "\n- Prioritize measurable metrics and quantifiable impacts"
                "\n- Use data-driven analysis where possible"
                "\n- Consider financial implications and empirical evidence"
                "\n- Present comparative data in tables or matrices when helpful"
            )
        elif criteria_focus == "qualitative":
            prompt += (
                "\n\nFocus on qualitative criteria:"
                "\n- Emphasize factors like user experience, cultural fit, and stakeholder feedback"
                "\n- Consider ethical implications and value alignment"
                "\n- Evaluate subjective but important considerations"
                "\n- Acknowledge where judgment and expertise supplement data"
            )

        # Add formality guidance
        if formality == "formal":
            prompt += (
                "\n\nProvide a formal analysis:"
                "\n- Use structured frameworks and methodologies"
                "\n- Present comprehensive assessment with clearly defined sections"
                "\n- Include executive summary and detailed analysis"
                "\n- Maintain professional, objective tone throughout"
            )
        elif formality == "informal":
            prompt += (
                "\n\nProvide an informal analysis:"
                "\n- Use a conversational, accessible approach"
                "\n- Focus on clear, practical insights"
                "\n- Highlight key considerations without excessive structure"
                "\n- Balance thoroughness with conciseness"
            )

        # Add reasoning pattern integration
        reasoning_pattern = kwargs.get("reasoning_pattern", "debate")
        if reasoning_pattern:
            pattern = self.reasoning_library.get_pattern(reasoning_pattern)
            if pattern:
                reasoning_prompt = pattern.generate_system_prompt(
                    domain="decision_making"
                )
                prompt += f"\n\n{reasoning_prompt}"

        return prompt

    def generate_task_prompt(self, task: str, **kwargs) -> str:
        """Generate a task prompt for decision support."""
        options = kwargs.get("options", [])
        criteria = kwargs.get("criteria", [])
        constraints = kwargs.get("constraints", [])
        reasoning_pattern = kwargs.get("reasoning_pattern", "debate")

        # Build task prompt
        prompt = f"Please provide decision support for the following situation:\n\n{task}\n\n"

        if options:
            prompt += "Options to consider:\n"
            for i, option in enumerate(options, 1):
                prompt += f"{i}. {option}\n"
            prompt += "\n"

        if criteria:
            prompt += "Key decision criteria:\n"
            for i, criterion in enumerate(criteria, 1):
                prompt += f"{i}. {criterion}\n"
            prompt += "\n"

        if constraints:
            prompt += "Important constraints:\n"
            for i, constraint in enumerate(constraints, 1):
                prompt += f"{i}. {constraint}\n"
            prompt += "\n"

        # Add reasoning pattern
        if reasoning_pattern:
            pattern = self.reasoning_library.get_pattern(reasoning_pattern)
            if pattern:
                reasoning_prompt = pattern.generate_task_prompt(
                    "Analyze these options to support a decision",
                    domain="decision_making",
                )
                prompt += f"{reasoning_prompt}\n\n"

        prompt += (
            "Your response should include:\n"
            "1. Clear analysis of each option's strengths and weaknesses\n"
            "2. Evaluation against the key criteria\n"
            "3. Discussion of trade-offs and potential risks\n"
            "4. Recommended decision with rationale\n"
            "5. Any implementation considerations or next steps\n"
        )

        return prompt

    def process_result(self, result: str) -> Dict[str, Any]:
        """Process decision support result."""
        # Extract option analyses
        options_analyses = []

        # Try to find option sections
        option_matches = re.findall(
            r"(?:^|\n)(?:Option|Alternative)\s+\d+:?(.*?)(?=\n(?:Option|Alternative|$))",
            result,
            re.DOTALL,
        )

        for option_text in option_matches:
            # Extract option details
            option_details = {}

            # Look for strengths and weaknesses
            strengths_match = re.search(
                r"(?:Strengths?|Pros?):?\s*(.*?)(?=\n(?:Weaknesses?|Cons?|Risks?|$))",
                option_text,
                re.IGNORECASE | re.DOTALL,
            )
            weaknesses_match = re.search(
                r"(?:Weaknesses?|Cons?|Risks?):?\s*(.*?)(?=\n(?:Strengths?|Pros?|$))",
                option_text,
                re.IGNORECASE | re.DOTALL,
            )

            if strengths_match:
                option_details["strengths"] = strengths_match.group(1).strip()
            if weaknesses_match:
                option_details["weaknesses"] = weaknesses_match.group(1).strip()

            options_analyses.append(option_details)

        return {
            "task_pattern": "decision_support",
            "options_analyses": options_analyses,
            "full_response": result,
        }
