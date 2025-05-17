import logging
from typing import Dict, Any, List, Optional, Union
import json

logger = logging.getLogger(__name__)

class ReasoningPattern:
    """Base class for reasoning patterns."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize the reasoning pattern.
        
        Args:
            name: Name of the reasoning pattern
            description: Description of the reasoning pattern
        """
        self.name = name
        self.description = description
    
    def generate_system_prompt(self, **kwargs) -> str:
        """
        Generate a system prompt for this reasoning pattern.
        
        Args:
            **kwargs: Additional parameters for prompt generation
            
        Returns:
            System prompt
        """
        raise NotImplementedError("Subclasses must implement generate_system_prompt")
    
    def generate_task_prompt(self, task: str, **kwargs) -> str:
        """
        Generate a task prompt for this reasoning pattern.
        
        Args:
            task: Task description
            **kwargs: Additional parameters for prompt generation
            
        Returns:
            Task prompt
        """
        raise NotImplementedError("Subclasses must implement generate_task_prompt")
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse a response using this reasoning pattern.
        
        Args:
            response: Response text
            
        Returns:
            Parsed response
        """
        raise NotImplementedError("Subclasses must implement parse_response")


class ChainOfThoughtPattern(ReasoningPattern):
    """
    Chain-of-Thought reasoning pattern.
    Promotes step-by-step reasoning for complex problem-solving.
    """
    
    def __init__(self):
        """Initialize the Chain-of-Thought pattern."""
        super().__init__(
            name="Chain of Thought",
            description="Step-by-step reasoning approach for complex problem-solving"
        )
    
    def generate_system_prompt(self, **kwargs) -> str:
        """Generate a system prompt for Chain-of-Thought reasoning."""
        verbosity = kwargs.get("verbosity", "medium")
        domain = kwargs.get("domain", "general")
        
        # Base prompt
        prompt = (
            "You are an AI assistant that uses step-by-step reasoning to solve complex problems. "
            "For each task, break down your thinking process into clear logical steps. "
            "Carefully consider each step before moving to the next one. "
            "Think about the problem systematically, considering different aspects and approaches."
        )
        
        # Add domain-specific instructions
        if domain == "math":
            prompt += (
                " When solving mathematical problems, start by identifying the known variables and what you need to find. "
                "Write out equations, show your work for each step of the calculation, and verify your answer."
            )
        elif domain == "reasoning":
            prompt += (
                " When solving logical reasoning problems, identify the premises and the conclusion. "
                "Analyze the logical structure, consider different possible interpretations, and evaluate the argument's validity."
            )
        elif domain == "code":
            prompt += (
                " When solving coding problems, start by understanding the requirements and breaking down the task. "
                "Plan your approach, consider edge cases, implement the solution step by step, and test with examples."
            )
        
        # Adjust verbosity
        if verbosity == "high":
            prompt += (
                " Be thorough and detailed in your explanations. Explicitly state your assumptions, "
                "consider multiple approaches, and explain why you chose a particular path."
            )
        elif verbosity == "low":
            prompt += (
                " Keep your reasoning concise but complete. Focus on the key steps and insights "
                "without unnecessary elaboration."
            )
        
        return prompt
    
    def generate_task_prompt(self, task: str, **kwargs) -> str:
        """Generate a task prompt for Chain-of-Thought reasoning."""
        # Add instruction to think step by step
        return (
            f"{task}\n\n"
            f"Think through this step-by-step:\n"
            f"1. First, understand what is being asked.\n"
            f"2. Break down the problem into parts.\n"
            f"3. Work through each part systematically.\n"
            f"4. Combine the results to reach your final answer."
        )
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse a Chain-of-Thought response."""
        # Find steps in the response
        import re
        
        # Look for numbered steps or step-by-step sections
        steps = []
        
        # Try to find numbered steps (e.g., "1.", "Step 1:", etc.)
        step_matches = re.findall(r"(?:^|\n)(?:Step\s*)?(\d+)[:.)\s]+(.*?)(?=(?:\n(?:Step\s*)?(?:\d+)[:.)\s]+)|$)", response, re.DOTALL)
        if step_matches:
            steps = [step.strip() for _, step in step_matches]
        
        # If no numbered steps found, try to split by newlines and filter for meaningful content
        if not steps:
            lines = response.split("\n")
            steps = [line.strip() for line in lines if line.strip() and len(line.strip()) > 10]
        
        # Extract the final answer if present
        final_answer = ""
        answer_match = re.search(r"(?:^|\n)(?:Answer:|Final Answer:|Therefore,|Thus,|In conclusion,)(.*?)(?:\n|$)", response, re.IGNORECASE | re.DOTALL)
        if answer_match:
            final_answer = answer_match.group(1).strip()
        
        return {
            "reasoning_pattern": "chain_of_thought",
            "steps": steps,
            "final_answer": final_answer,
            "full_response": response
        }


class TreeOfThoughtsPattern(ReasoningPattern):
    """
    Tree of Thoughts reasoning pattern.
    Explores multiple reasoning paths and evaluates them to find the best solution.
    """
    
    def __init__(self):
        """Initialize the Tree of Thoughts pattern."""
        super().__init__(
            name="Tree of Thoughts",
            description="Multi-path reasoning that explores and evaluates different approaches"
        )
    
    def generate_system_prompt(self, **kwargs) -> str:
        """Generate a system prompt for Tree of Thoughts reasoning."""
        breadth = kwargs.get("breadth", 3)  # Number of paths to explore
        depth = kwargs.get("depth", 2)  # Depth of exploration
        domain = kwargs.get("domain", "general")
        
        prompt = (
            f"You are an AI assistant that uses tree-of-thoughts reasoning to solve complex problems. "
            f"For each task, generate {breadth} different approaches or starting points. "
            f"Then explore each approach for up to {depth} steps, evaluating which paths are most promising. "
            f"Finally, select the best path and complete the solution."
        )
        
        # Add domain-specific instructions
        if domain == "creative":
            prompt += (
                " For creative tasks, generate diverse and novel approaches. "
                "Consider unusual perspectives and combinations of ideas. "
                "Evaluate paths based on originality, coherence, and relevance."
            )
        elif domain == "strategic":
            prompt += (
                " For strategic tasks, consider different scenarios and outcomes. "
                "Evaluate paths based on risk, reward, and long-term implications. "
                "Consider both offensive and defensive strategies."
            )
        elif domain == "research":
            prompt += (
                " For research tasks, explore multiple hypotheses or frameworks. "
                "Evaluate paths based on evidence, explanatory power, and consistency with known facts. "
                "Consider how to test or validate each approach."
            )
        
        return prompt
    
    def generate_task_prompt(self, task: str, **kwargs) -> str:
        """Generate a task prompt for Tree of Thoughts reasoning."""
        breadth = kwargs.get("breadth", 3)
        
        return (
            f"{task}\n\n"
            f"Explore multiple approaches to this problem:\n\n"
            f"1. First, generate {breadth} different ways to tackle this problem.\n"
            f"2. For each approach, explore the implications and next steps.\n"
            f"3. Evaluate which approach is most promising.\n"
            f"4. Develop the best approach into a complete solution."
        )
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse a Tree of Thoughts response."""
        import re
        
        # Try to identify the different approaches/paths
        paths = []
        
        # Look for approach headers (e.g., "Approach 1:", "Path A:", etc.)
        path_matches = re.findall(r"(?:^|\n)(?:Approach|Path)\s*(?:\d+|[A-Z])[:.)\s]+(.*?)(?=(?:\n(?:Approach|Path)\s*(?:\d+|[A-Z])[:.)\s]+)|(?:\n(?:Evaluation|Comparing))|$)", response, re.DOTALL)
        
        if path_matches:
            paths = [path.strip() for path in path_matches]
        
        # Extract evaluation if present
        evaluation = ""
        eval_match = re.search(r"(?:^|\n)(?:Evaluation:|Comparing paths:|Comparing approaches:)(.*?)(?=\n(?:Selected path:|Best approach:|Conclusion:)|$)", response, re.IGNORECASE | re.DOTALL)
        if eval_match:
            evaluation = eval_match.group(1).strip()
        
        # Extract the selected path/conclusion
        selected_path = ""
        selected_match = re.search(r"(?:^|\n)(?:Selected path:|Best approach:|Conclusion:)(.*?)$", response, re.IGNORECASE | re.DOTALL)
        if selected_match:
            selected_path = selected_match.group(1).strip()
        
        return {
            "reasoning_pattern": "tree_of_thoughts",
            "paths": paths,
            "evaluation": evaluation,
            "selected_path": selected_path,
            "full_response": response
        }


class SelfReflectionPattern(ReasoningPattern):
    """
    Self-Reflection reasoning pattern.
    Generates a solution, then critically evaluates and refines it.
    """
    
    def __init__(self):
        """Initialize the Self-Reflection pattern."""
        super().__init__(
            name="Self-Reflection",
            description="Critical evaluation and refinement of initial solutions"
        )
    
    def generate_system_prompt(self, **kwargs) -> str:
        """Generate a system prompt for Self-Reflection reasoning."""
        iterations = kwargs.get("iterations", 2)
        domain = kwargs.get("domain", "general")
        
        prompt = (
            f"You are an AI assistant that uses self-reflection to produce high-quality solutions. "
            f"For each task, you will:\n"
            f"1. Generate an initial solution\n"
            f"2. Critically evaluate your solution, identifying strengths and weaknesses\n"
            f"3. Refine your solution based on this reflection\n"
            f"Repeat this process {iterations} times to progressively improve your answer."
        )
        
        # Add domain-specific instructions
        if domain == "writing":
            prompt += (
                " For writing tasks, evaluate clarity, coherence, tone, and impact. "
                "Identify passages that could be confusing or ambiguous. "
                "Look for opportunities to strengthen arguments or make language more engaging."
            )
        elif domain == "analysis":
            prompt += (
                " For analytical tasks, evaluate completeness, logical consistency, and potential biases. "
                "Consider alternative interpretations and counterarguments. "
                "Look for unstated assumptions or gaps in reasoning."
            )
        elif domain == "decision_making":
            prompt += (
                " For decision-making tasks, evaluate the criteria used, consideration of alternatives, "
                "and potential consequences. Look for biases like short-term thinking or overconfidence. "
                "Consider how different stakeholders would view the decision."
            )
        
        return prompt
    
    def generate_task_prompt(self, task: str, **kwargs) -> str:
        """Generate a task prompt for Self-Reflection reasoning."""
        return (
            f"{task}\n\n"
            f"Please approach this task using self-reflection:\n\n"
            f"1. Initial solution: Provide your first attempt at solving this problem.\n\n"
            f"2. Reflection: Critically evaluate your solution. What are its strengths and weaknesses? "
            f"What assumptions did you make? What might you have missed?\n\n"
            f"3. Refined solution: Based on your reflection, provide an improved solution."
        )
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse a Self-Reflection response."""
        import re
        
        # Extract initial solution, reflections, and refined solution
        initial_solution = ""
        init_match = re.search(r"(?:^|\n)(?:Initial solution:|First attempt:|Initial answer:)(.*?)(?=\n(?:Reflection:|Self-critique:|Evaluation:))", response, re.IGNORECASE | re.DOTALL)
        if init_match:
            initial_solution = init_match.group(1).strip()
        
        reflection = ""
        refl_match = re.search(r"(?:^|\n)(?:Reflection:|Self-critique:|Evaluation:)(.*?)(?=\n(?:Refined solution:|Improved answer:|Final solution:))", response, re.IGNORECASE | re.DOTALL)
        if refl_match:
            reflection = refl_match.group(1).strip()
        
        refined_solution = ""
        refine_match = re.search(r"(?:^|\n)(?:Refined solution:|Improved answer:|Final solution:)(.*?)$", response, re.IGNORECASE | re.DOTALL)
        if refine_match:
            refined_solution = refine_match.group(1).strip()
        
        return {
            "reasoning_pattern": "self_reflection",
            "initial_solution": initial_solution,
            "reflection": reflection,
            "refined_solution": refined_solution,
            "full_response": response
        }


class ScientificMethodPattern(ReasoningPattern):
    """
    Scientific Method reasoning pattern.
    Structures reasoning as hypothesis formulation, testing, and refinement.
    """
    
    def __init__(self):
        """Initialize the Scientific Method pattern."""
        super().__init__(
            name="Scientific Method",
            description="Structured reasoning based on hypothesis formulation and testing"
        )
    
    def generate_system_prompt(self, **kwargs) -> str:
        """Generate a system prompt for Scientific Method reasoning."""
        domain = kwargs.get("domain", "general")
        
        prompt = (
            "You are an AI assistant that uses scientific method reasoning to solve problems. "
            "For each task, apply a structured scientific approach:\n"
            "1. Observe: Gather and analyze relevant information\n"
            "2. Question: Identify the specific question or problem to address\n"
            "3. Hypothesize: Formulate testable explanations or solutions\n"
            "4. Predict: Determine what should happen if the hypothesis is correct\n"
            "5. Test: Analyze the hypothesis against available data or logical implications\n"
            "6. Conclude: Draw conclusions based on the testing results\n"
            "7. Refine: Improve the hypothesis based on the results"
        )
        
        # Add domain-specific instructions
        if domain == "data_analysis":
            prompt += (
                " For data analysis tasks, examine the dataset properties first. "
                "Formulate hypotheses about patterns or relationships in the data. "
                "Test using appropriate statistical methods and validate against subsets of data. "
                "Consider alternative explanations for observed patterns."
            )
        elif domain == "problem_diagnosis":
            prompt += (
                " For diagnostic tasks, gather all symptoms or error conditions. "
                "Formulate hypotheses about potential root causes. "
                "Test each hypothesis by checking its implications against the observed symptoms. "
                "Prioritize tests that can quickly eliminate multiple hypotheses."
            )
        elif domain == "prediction":
            prompt += (
                " For prediction tasks, examine historical data and context first. "
                "Formulate hypotheses about causal factors and their relationships. "
                "Test predictions against known outcomes in similar situations. "
                "Consider multiple scenarios with different probability weights."
            )
        
        return prompt
    
    def generate_task_prompt(self, task: str, **kwargs) -> str:
        """Generate a task prompt for Scientific Method reasoning."""
        return (
            f"{task}\n\n"
            f"Please approach this using the scientific method:\n\n"
            f"1. Observation: What information is available or relevant?\n\n"
            f"2. Question: What specific problem needs to be solved?\n\n"
            f"3. Hypothesis: What are potential explanations or solutions?\n\n"
            f"4. Prediction: What should happen if each hypothesis is correct?\n\n"
            f"5. Testing: How do the hypotheses hold up against available information?\n\n"
            f"6. Conclusion: What is the best supported explanation or solution?\n\n"
            f"7. Refinement: How could this solution be improved with more information?"
        )
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse a Scientific Method response."""
        import re
        
        # Extract each section of the scientific method
        observation = ""
        obs_match = re.search(r"(?:^|\n)(?:1\.|Observation:|Observations:)(.*?)(?=(?:\n(?:2\.|Question:|Questions:)))", response, re.IGNORECASE | re.DOTALL)
        if obs_match:
            observation = obs_match.group(1).strip()
        
        question = ""
        q_match = re.search(r"(?:^|\n)(?:2\.|Question:|Questions:)(.*?)(?=(?:\n(?:3\.|Hypothesis:|Hypotheses:)))", response, re.IGNORECASE | re.DOTALL)
        if q_match:
            question = q_match.group(1).strip()
        
        hypothesis = ""
        h_match = re.search(r"(?:^|\n)(?:3\.|Hypothesis:|Hypotheses:)(.*?)(?=(?:\n(?:4\.|Prediction:|Predictions:)))", response, re.IGNORECASE | re.DOTALL)
        if h_match:
            hypothesis = h_match.group(1).strip()
        
        prediction = ""
        p_match = re.search(r"(?:^|\n)(?:4\.|Prediction:|Predictions:)(.*?)(?=(?:\n(?:5\.|Testing:|Test:)))", response, re.IGNORECASE | re.DOTALL)
        if p_match:
            prediction = p_match.group(1).strip()
        
        testing = ""
        t_match = re.search(r"(?:^|\n)(?:5\.|Testing:|Test:)(.*?)(?=(?:\n(?:6\.|Conclusion:|Conclusions:)))", response, re.IGNORECASE | re.DOTALL)
        if t_match:
            testing = t_match.group(1).strip()
        
        conclusion = ""
        c_match = re.search(r"(?:^|\n)(?:6\.|Conclusion:|Conclusions:)(.*?)(?=(?:\n(?:7\.|Refinement:|Refinements:))|\Z)", response, re.IGNORECASE | re.DOTALL)
        if c_match:
            conclusion = c_match.group(1).strip()
        
        refinement = ""
        r_match = re.search(r"(?:^|\n)(?:7\.|Refinement:|Refinements:)(.*?)$", response, re.IGNORECASE | re.DOTALL)
        if r_match:
            refinement = r_match.group(1).strip()
        
        return {
            "reasoning_pattern": "scientific_method",
            "observation": observation,
            "question": question,
            "hypothesis": hypothesis,
            "prediction": prediction,
            "testing": testing,
            "conclusion": conclusion,
            "refinement": refinement,
            "full_response": response
        }


class DebatePattern(ReasoningPattern):
    """
    Debate reasoning pattern.
    Considers multiple perspectives by simulating a debate between different viewpoints.
    """
    
    def __init__(self):
        """Initialize the Debate pattern."""
        super().__init__(
            name="Debate",
            description="Exploration of multiple perspectives through simulated debate"
        )
    
    def generate_system_prompt(self, **kwargs) -> str:
        """Generate a system prompt for Debate reasoning."""
        perspectives = kwargs.get("perspectives", 2)
        domain = kwargs.get("domain", "general")
        
        prompt = (
            f"You are an AI assistant that uses debate reasoning to explore multiple perspectives on complex issues. "
            f"For each task, simulate a constructive debate between {perspectives} different viewpoints. "
            f"Present the strongest version of each perspective, including its key arguments and evidence. "
            f"After presenting all perspectives, provide a balanced synthesis that acknowledges the strengths and limitations of each view."
        )
        
        # Add domain-specific instructions
        if domain == "ethical":
            prompt += (
                " For ethical questions, consider perspectives from different ethical frameworks "
                "(e.g., consequentialism, deontology, virtue ethics) and different stakeholders. "
                "Acknowledge value trade-offs and areas of moral uncertainty."
            )
        elif domain == "policy":
            prompt += (
                " For policy questions, consider perspectives from different ideological positions, "
                "different expert domains (e.g., economics, law, public health), and different affected groups. "
                "Discuss short-term and long-term implications."
            )
        elif domain == "scientific":
            prompt += (
                " For scientific questions, consider mainstream scientific views, credible minority positions, "
                "and where applicable, historical perspectives on how scientific understanding has evolved. "
                "Distinguish between established facts, leading hypotheses, and speculative ideas."
            )
        
        return prompt
    
    def generate_task_prompt(self, task: str, **kwargs) -> str:
        """Generate a task prompt for Debate reasoning."""
        perspectives = kwargs.get("perspectives", ["Perspective A", "Perspective B"])
        
        prompt = f"{task}\n\n" + "Please explore this through a constructive debate format:\n\n"
        
        for i, perspective in enumerate(perspectives, 1):
            prompt += f"{i}. {perspective}: Present key arguments and evidence.\n\n"
        
        prompt += "Synthesis: Provide a balanced analysis incorporating insights from all perspectives."
        
        return prompt
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse a Debate response."""
        import re
        
        # Extract different perspectives and the synthesis
        perspectives = []
        
        # Look for perspective headers (e.g., "Perspective A:", "First perspective:", etc.)
        perspective_pattern = r"(?:^|\n)(?:Perspective\s+[A-Za-z]|(?:First|Second|Third|Fourth|Fifth)\s+perspective|Viewpoint\s+\d+)[:\s]+(.*?)(?=(?:\n(?:Perspective\s+[A-Za-z]|(?:First|Second|Third|Fourth|Fifth)\s+perspective|Viewpoint\s+\d+|Synthesis:|Conclusion:|Balance:|Integrated view:))|$)"
        
        perspective_matches = re.findall(perspective_pattern, response, re.IGNORECASE | re.DOTALL)
        
        if perspective_matches:
            perspectives = [p.strip() for p in perspective_matches]
        
        # Extract synthesis
        synthesis = ""
        synth_match = re.search(r"(?:^|\n)(?:Synthesis:|Conclusion:|Balance:|Integrated view:)(.*?)$", response, re.IGNORECASE | re.DOTALL)
        if synth_match:
            synthesis = synth_match.group(1).strip()
        
        return {
            "reasoning_pattern": "debate",
            "perspectives": perspectives,
            "synthesis": synthesis,
            "full_response": response
        }


class FirstPrinciplesPattern(ReasoningPattern):
    """
    First Principles reasoning pattern.
    Breaks down complex problems to fundamental truths and rebuilds from there.
    """
    
    def __init__(self):
        """Initialize the First Principles pattern."""
        super().__init__(
            name="First Principles",
            description="Reasoning from fundamental truths rather than by analogy"
        )
    
    def generate_system_prompt(self, **kwargs) -> str:
        """Generate a system prompt for First Principles reasoning."""
        domain = kwargs.get("domain", "general")
        
        prompt = (
            "You are an AI assistant that uses first principles reasoning to solve complex problems. "
            "Instead of relying on analogies, conventions, or assumptions, you break down problems "
            "into their most basic, foundational elements and truths. Then you rebuild a solution "
            "from those fundamentals. Your analysis should identify and challenge any hidden assumptions, "
            "focusing on what is logically necessary and sufficient."
        )
        
        # Add domain-specific instructions
        if domain == "engineering":
            prompt += (
                " For engineering problems, identify the fundamental physical laws and constraints that apply. "
                "Challenge conventional designs and approaches. Ask what the essential function is and "
                "consider multiple ways to achieve it from basic principles."
            )
        elif domain == "business":
            prompt += (
                " For business problems, identify fundamental economic principles and customer needs. "
                "Question industry conventions and business models. Consider the essential value being created "
                "and different ways to deliver and capture that value."
            )
        elif domain == "conceptual":
            prompt += (
                " For conceptual problems, identify the most basic definitions and axioms relevant to the domain. "
                "Challenge conventional frameworks and categories. Build up new conceptual structures "
                "that are minimally sufficient to address the problem."
            )
        
        return prompt
    
    def generate_task_prompt(self, task: str, **kwargs) -> str:
        """Generate a task prompt for First Principles reasoning."""
        return (
            f"{task}\n\n"
            f"Please approach this using first principles reasoning:\n\n"
            f"1. Identify fundamental truths: What are the most basic facts or principles relevant to this problem?\n\n"
            f"2. Challenge assumptions: What conventional wisdom or assumptions might be limiting our thinking?\n\n"
            f"3. Break down the problem: Reduce the problem to its essential elements.\n\n"
            f"4. Rebuild: Construct a solution using only what is logically necessary.\n\n"
            f"5. Verify: Check that your solution addresses the fundamental requirements without unnecessary complications."
        )
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse a First Principles response."""
        import re
        
        # Extract the different sections
        fundamentals = ""
        fund_match = re.search(r"(?:^|\n)(?:1\.|Fundamental truths:|Basic principles:|Foundational elements:)(.*?)(?=(?:\n(?:2\.|Challenge assumptions:|Assumptions:|Challenging conventions:)))", response, re.IGNORECASE | re.DOTALL)
        if fund_match:
            fundamentals = fund_match.group(1).strip()
        
        assumptions = ""
        assume_match = re.search(r"(?:^|\n)(?:2\.|Challenge assumptions:|Assumptions:|Challenging conventions:)(.*?)(?=(?:\n(?:3\.|Break down:|Problem breakdown:|Essential elements:)))", response, re.IGNORECASE | re.DOTALL)
        if assume_match:
            assumptions = assume_match.group(1).strip()
        
        breakdown = ""
        break_match = re.search(r"(?:^|\n)(?:3\.|Break down:|Problem breakdown:|Essential elements:)(.*?)(?=(?:\n(?:4\.|Rebuild:|Solution construction:|Building from fundamentals:)))", response, re.IGNORECASE | re.DOTALL)
        if break_match:
            breakdown = break_match.group(1).strip()
        
        solution = ""
        sol_match = re.search(r"(?:^|\n)(?:4\.|Rebuild:|Solution construction:|Building from fundamentals:)(.*?)(?=(?:\n(?:5\.|Verify:|Verification:|Solution check:))|\Z)", response, re.IGNORECASE | re.DOTALL)
        if sol_match:
            solution = sol_match.group(1).strip()
        
        verification = ""
        ver_match = re.search(r"(?:^|\n)(?:5\.|Verify:|Verification:|Solution check:)(.*?)$", response, re.IGNORECASE | re.DOTALL)
        if ver_match:
            verification = ver_match.group(1).strip()
        
        return {
            "reasoning_pattern": "first_principles",
            "fundamental_truths": fundamentals,
            "challenged_assumptions": assumptions,
            "problem_breakdown": breakdown,
            "rebuilt_solution": solution,
            "verification": verification,
            "full_response": response
        }


class ReasoningPatternLibrary:
    """Library of reasoning patterns that can be applied to different domains."""
    
    def __init__(self):
        """Initialize the reasoning pattern library."""
        self.patterns = {
            "chain_of_thought": ChainOfThoughtPattern(),
            "tree_of_thoughts": TreeOfThoughtsPattern(),
            "self_reflection": SelfReflectionPattern(),
            "scientific_method": ScientificMethodPattern(),
            "debate": DebatePattern(),
            "first_principles": FirstPrinciplesPattern()
        }
    
    def get_pattern(self, pattern_name: str) -> Optional[ReasoningPattern]:
        """
        Get a reasoning pattern by name.
        
        Args:
            pattern_name: Name of the reasoning pattern
            
        Returns:
            Reasoning pattern instance or None if not found
        """
        return self.patterns.get(pattern_name.lower().replace(" ", "_"))
    
    def list_patterns(self) -> List[Dict[str, str]]:
        """
        List all available reasoning patterns.
        
        Returns:
            List of pattern information dictionaries
        """
        return [
            {"name": pattern.name, "description": pattern.description}
            for pattern in self.patterns.values()
        ]
    
    def recommend_pattern(self, task: str, domain: str) -> Dict[str, Any]:
        """
        Recommend a reasoning pattern for a given task and domain.
        
        Args:
            task: Task description
            domain: Domain of the task
            
        Returns:
            Recommendation with pattern and reasoning
        """
        # Simple keyword-based recommendation
        keywords = {
            "chain_of_thought": ["step by step", "sequential", "process", "logical", "procedure", "algorithm"],
            "tree_of_thoughts": ["alternatives", "options", "paths", "approaches", "compare", "multiple"],
            "self_reflection": ["improve", "refine", "critique", "evaluate", "review", "assess"],
            "scientific_method": ["hypothesis", "experiment", "test", "evidence", "data", "observation"],
            "debate": ["perspectives", "viewpoints", "arguments", "controversial", "opinion", "debate"],
            "first_principles": ["fundamental", "assumption", "basic", "simplify", "essential", "core"]
        }
        
        # Domain affinities
        domain_affinities = {
            "math": ["chain_of_thought", "scientific_method", "first_principles"],
            "writing": ["self_reflection", "tree_of_thoughts"],
            "ethics": ["debate", "self_reflection"],
            "engineering": ["first_principles", "scientific_method"],
            "business": ["tree_of_thoughts", "debate"],
            "research": ["scientific_method", "debate"]
        }
        
        # Count keyword matches
        scores = {pattern_name: 0 for pattern_name in self.patterns.keys()}
        
        # Keyword matching
        task_lower = task.lower()
        for pattern_name, pattern_keywords in keywords.items():
            for keyword in pattern_keywords:
                if keyword in task_lower:
                    scores[pattern_name] += 1
        
        # Domain affinity
        domain_lower = domain.lower()
        for d, patterns in domain_affinities.items():
            if d in domain_lower:
                for pattern in patterns:
                    scores[pattern] += 2
        
        # Get top recommendation
        if not any(scores.values()):
            # Default to chain of thought if no clear winner
            top_pattern = "chain_of_thought"
            reasoning = "No specific indicators found. Chain of Thought is a versatile default approach."
        else:
            top_pattern = max(scores.items(), key=lambda x: x[1])[0]
            
            # Generate reasoning
            matching_keywords = [k for k in keywords[top_pattern] if k in task_lower]
            matching_domains = [d for d, patterns in domain_affinities.items() if d in domain_lower and top_pattern in patterns]
            
            reasoning_parts = []
            if matching_keywords:
                reasoning_parts.append(f"Task contains relevant keywords: {', '.join(matching_keywords)}.")
            if matching_domains:
                reasoning_parts.append(f"Task domain ({domain}) has affinity with this pattern.")
            
            reasoning = " ".join(reasoning_parts) if reasoning_parts else "Best overall match for the given task and domain."
        
        return {
            "recommended_pattern": top_pattern,
            "pattern_instance": self.patterns[top_pattern],
            "reasoning": reasoning,
            "scores": scores
        }
    
    def apply_pattern(
        self,
        pattern_name: str,
        task: str,
        agent_type: str = "planner",
        **kwargs
    ) -> Dict[str, str]:
        """
        Apply a reasoning pattern to a task for a specific agent type.
        
        Args:
            pattern_name: Name of the reasoning pattern
            task: Task description
            agent_type: Type of agent (planner, executor, critic)
            **kwargs: Additional parameters for the pattern
            
        Returns:
            Dictionary with system prompt and task prompt
        """
        pattern = self.get_pattern(pattern_name)
        if not pattern:
            raise ValueError(f"Pattern '{pattern_name}' not found")
        
        # Generate prompts
        system_prompt = pattern.generate_system_prompt(**kwargs)
        task_prompt = pattern.generate_task_prompt(task, **kwargs)
        
        # Adjust for agent type
        if agent_type == "planner":
            system_prompt += "\nYour primary responsibility is to create effective plans and strategies."
        elif agent_type == "executor":
            system_prompt += "\nYour primary responsibility is to implement solutions effectively."
        elif agent_type == "critic":
            system_prompt += "\nYour primary responsibility is to evaluate outputs critically and provide constructive feedback."
        
        return {
            "system_prompt": system_prompt,
            "task_prompt": task_prompt,
            "pattern": pattern_name
        }


# Domain-specific preset configurations
DOMAIN_PRESETS = {
    "mathematical_problem_solving": {
        "pattern": "chain_of_thought",
        "domain": "math",
        "verbosity": "high"
    },
    "creative_writing": {
        "pattern": "tree_of_thoughts",
        "domain": "creative",
        "breadth": 3,
        "depth": 2
    },
    "ethical_analysis": {
        "pattern": "debate",
        "domain": "ethical",
        "perspectives": ["Consequentialist", "Deontological", "Virtue Ethics"]
    },
    "scientific_research": {
        "pattern": "scientific_method",
        "domain": "research"
    },
    "business_strategy": {
        "pattern": "first_principles",
        "domain": "business"
    },
    "content_creation": {
        "pattern": "self_reflection",
        "domain": "writing",
        "iterations": 2
    },
    "engineering_design": {
        "pattern": "first_principles",
        "domain": "engineering"
    },
    "policy_analysis": {
        "pattern": "debate",
        "domain": "policy",
        "perspectives": ["Economic", "Social", "Environmental", "Political"]
    }
}