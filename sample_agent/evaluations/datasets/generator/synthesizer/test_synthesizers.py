#!/usr/bin/env python3
"""
Test Suite for Synthetic Data Generators
----------------------------------------

Comprehensive test suite for the unified synthetic data generation architecture.
Tests both CustomSynthesizer and DeepEvalSynthesizer with various configurations.
"""

import asyncio
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import sys

# Add path to import agents
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from sample_agent.evaluations.datasets.generator.synthesizer import (
    BaseSynthesizer,
    CustomSynthesizer,
    DeepEvalSynthesizer,
    SynthesizerConfig,
    SyntheticExample,
    ExecutionMode,
    DatasetPersistence,
    LangSmithPersistence
)


class MockWorkflow:
    """Mock workflow for testing"""
    
    def __init__(self):
        self.invoke_count = 0
        
    async def ainvoke(self, input_data: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        self.invoke_count += 1
        return {
            "messages": [
                {"role": "assistant", "content": f"Mock response to: {input_data.get('messages', [{}])[0].get('content', 'unknown')}"}
            ],
            "metadata": {"processed": True, "invoke_count": self.invoke_count}
        }


class MockPersistence:
    """Mock persistence for testing"""
    
    def __init__(self):
        self.saved_datasets = []
        
    async def save_dataset(self, examples: List[SyntheticExample], project_name: str) -> bool:
        self.saved_datasets.append({
            "project_name": project_name,
            "examples": examples,
            "count": len(examples)
        })
        return True


@pytest.fixture
def base_config():
    """Base configuration for testing"""
    return SynthesizerConfig(
        project_name="test-project",
        tags=["test", "synthetic"],
        trace_metadata={"environment": "test", "version": "1.0"},
        num_scenarios=2
    )


@pytest.fixture
def mock_workflow():
    """Mock workflow for testing"""
    return MockWorkflow()


@pytest.fixture
def mock_persistence():
    """Mock persistence for testing"""
    return MockPersistence()


class TestBaseSynthesizer:
    """Test base synthesizer functionality"""
    
    def test_config_initialization(self, base_config):
        """Test configuration initialization"""
        
        class TestSynthesizer(BaseSynthesizer):
            async def generate_synthetic_dataset(self, workflow=None, num_scenarios=None):
                return []
                
        synthesizer = TestSynthesizer(base_config)
        
        assert synthesizer.config.project_name == "test-project"
        assert synthesizer.config.tags == ["test", "synthetic"]
        assert synthesizer.config.num_scenarios == 2
        
    def test_workflow_analysis_structure(self, base_config, mock_workflow):
        """Test workflow analysis structure"""
        
        class TestSynthesizer(BaseSynthesizer):
            async def generate_synthetic_dataset(self, workflow=None, num_scenarios=None):
                return []
                
        synthesizer = TestSynthesizer(base_config)
        
        # Test workflow analysis (should not fail)
        analysis = synthesizer.analyze_workflow_structure(mock_workflow)
        
        assert isinstance(analysis, dict)
        assert "type" in analysis
        assert "workflow_description" in analysis


class TestCustomSynthesizer:
    """Test CustomSynthesizer functionality"""
    
    def test_initialization_modes(self, base_config):
        """Test initialization with different modes"""
        
        # Test default mode (EXECUTION)
        synthesizer_default = CustomSynthesizer(base_config)
        assert synthesizer_default.mode == ExecutionMode.EXECUTION
        
        # Test SYNTHETIC mode
        synthesizer_synthetic = CustomSynthesizer(base_config, mode=ExecutionMode.SYNTHETIC)
        assert synthesizer_synthetic.mode == ExecutionMode.SYNTHETIC
        
        # Test EXECUTION mode explicitly
        synthesizer_execution = CustomSynthesizer(base_config, mode=ExecutionMode.EXECUTION)
        assert synthesizer_execution.mode == ExecutionMode.EXECUTION
        
    @pytest.mark.asyncio
    async def test_synthetic_mode_generation(self, base_config, mock_workflow, mock_persistence):
        """Test synthetic mode generation"""
        
        synthesizer = CustomSynthesizer(base_config, mode=ExecutionMode.SYNTHETIC, persistence=mock_persistence)
        
        # Mock the LLM response for scenario generation
        with patch.object(synthesizer, 'generate_scenarios_from_workflow') as mock_scenarios:
            mock_scenarios.return_value = [
                {
                    "user_input": "Test input",
                    "expected_behavior": "Test behavior", 
                    "complexity": "simple",
                    "target_agents": ["test_agent"],
                    "required_tools": ["test_tool"],
                    "context": {}
                }
            ]
            
            # Mock synthetic response generation
            with patch.object(synthesizer, '_generate_synthetic_response') as mock_response:
                mock_response.return_value = {"messages": [{"role": "assistant", "content": "Synthetic response"}]}
                
                examples = await synthesizer.generate_synthetic_dataset(workflow=mock_workflow, num_scenarios=1)
                
                assert len(examples) == 1
                assert examples[0].metadata["execution_mode"] == "synthetic"
                assert "mode:synthetic" in examples[0].metadata["tags"]
                
    @pytest.mark.asyncio
    async def test_execution_mode_generation(self, base_config, mock_workflow, mock_persistence):
        """Test execution mode generation"""
        
        synthesizer = CustomSynthesizer(base_config, mode=ExecutionMode.EXECUTION, persistence=mock_persistence)
        
        # Mock the LLM response for scenario generation
        with patch.object(synthesizer, 'generate_scenarios_from_workflow') as mock_scenarios:
            mock_scenarios.return_value = [
                {
                    "user_input": "Test input",
                    "expected_behavior": "Test behavior",
                    "complexity": "simple",
                    "target_agents": ["test_agent"],
                    "required_tools": ["test_tool"],
                    "context": {}
                }
            ]
            
            examples = await synthesizer.generate_synthetic_dataset(workflow=mock_workflow, num_scenarios=1)
            
            assert len(examples) == 1
            assert examples[0].metadata["execution_mode"] == "execution"
            assert "mode:execution" in examples[0].metadata["tags"]
            # Should have invoked workflow once
            assert mock_workflow.invoke_count == 1
            
    @pytest.mark.asyncio
    async def test_workflow_required_error(self, base_config):
        """Test that workflow is required"""
        
        synthesizer = CustomSynthesizer(base_config)
        
        with pytest.raises(ValueError, match="CustomSynthesizer requires a workflow"):
            await synthesizer.generate_synthetic_dataset(workflow=None)


class TestDeepEvalSynthesizer:
    """Test DeepEvalSynthesizer functionality"""
    
    def test_initialization(self, base_config, mock_persistence):
        """Test initialization"""
        
        synthesizer = DeepEvalSynthesizer(base_config, persistence=mock_persistence)
        
        assert synthesizer.config.project_name == "test-project"
        assert synthesizer.persistence == mock_persistence
        assert synthesizer.synthesizer is None  # Not initialized until generation
        
    @pytest.mark.asyncio
    async def test_generate_without_workflow(self, base_config, mock_persistence):
        """Test generation without workflow"""
        
        synthesizer = DeepEvalSynthesizer(base_config, persistence=mock_persistence)
        
        # Mock DeepEval synthesizer
        mock_deepeval = Mock()
        mock_deepeval.synthetic_goldens = [
            Mock(input="Test input 1", expected_output="Test output 1"),
            Mock(input="Test input 2", expected_output="Test output 2")
        ]
        
        with patch('sample_agent.evaluations.datasets.generator.synthesizer.deepeval_synthesizer.Synthesizer') as mock_synthesizer_class:
            mock_synthesizer_class.return_value = mock_deepeval
            
            examples = await synthesizer.generate_synthetic_dataset(num_scenarios=2)
            
            assert len(examples) == 2
            assert all("generator:deepeval" in ex.metadata["tags"] for ex in examples)
            assert all("synthetic:generated" in ex.metadata["tags"] for ex in examples)
            
    @pytest.mark.asyncio
    async def test_generate_with_workflow_analysis(self, base_config, mock_workflow, mock_persistence):
        """Test generation with workflow analysis"""
        
        synthesizer = DeepEvalSynthesizer(base_config, persistence=mock_persistence)
        
        # Mock DeepEval synthesizer
        mock_deepeval = Mock()
        mock_deepeval.synthetic_goldens = [
            Mock(input="Test input", expected_output="Test output")
        ]
        
        with patch('sample_agent.evaluations.datasets.generator.synthesizer.deepeval_synthesizer.Synthesizer') as mock_synthesizer_class:
            mock_synthesizer_class.return_value = mock_deepeval
            
            examples = await synthesizer.generate_synthetic_dataset(
                workflow=mock_workflow,
                num_scenarios=1
            )
            
            assert len(examples) == 1
            assert examples[0].metadata["workflow_analysis"] is not None
            assert "generator:deepeval" in examples[0].metadata["tags"]
            
    @pytest.mark.asyncio
    async def test_custom_task_description(self, base_config, mock_persistence):
        """Test custom task description parameter"""
        
        synthesizer = DeepEvalSynthesizer(base_config, persistence=mock_persistence)
        
        # Mock DeepEval synthesizer
        mock_deepeval = Mock()
        mock_deepeval.synthetic_goldens = [
            Mock(input="Custom task input", expected_output="Custom task output")
        ]
        
        with patch('sample_agent.evaluations.datasets.generator.synthesizer.deepeval_synthesizer.Synthesizer') as mock_synthesizer_class:
            mock_synthesizer_class.return_value = mock_deepeval
            
            examples = await synthesizer.generate_synthetic_dataset(
                num_scenarios=1,
                task_description="Custom task for testing",
                scenario="Test scenario"
            )
            
            assert len(examples) == 1
            assert examples[0].metadata["generator"] == "DeepEvalSynthesizer"


class TestUnifiedInterface:
    """Test unified interface between synthesizers"""
    
    @pytest.mark.asyncio
    async def test_polymorphic_usage(self, base_config, mock_workflow, mock_persistence):
        """Test polymorphic usage of synthesizers"""
        
        # Both synthesizers should be usable as BaseSynthesizer
        custom_synthesizer: BaseSynthesizer = CustomSynthesizer(base_config, persistence=mock_persistence)
        deepeval_synthesizer: BaseSynthesizer = DeepEvalSynthesizer(base_config, persistence=mock_persistence)
        
        # Mock DeepEval for this test
        mock_deepeval = Mock()
        mock_deepeval.synthetic_goldens = [Mock(input="Test", expected_output="Test")]
        
        with patch('sample_agent.evaluations.datasets.generator.synthesizer.deepeval_synthesizer.Synthesizer') as mock_synthesizer_class:
            mock_synthesizer_class.return_value = mock_deepeval
            
            # Mock scenario generation for CustomSynthesizer
            with patch.object(custom_synthesizer, 'generate_scenarios_from_workflow') as mock_scenarios:
                mock_scenarios.return_value = [
                    {
                        "user_input": "Test input",
                        "expected_behavior": "Test behavior",
                        "complexity": "simple",
                        "target_agents": ["test_agent"],
                        "required_tools": ["test_tool"],
                        "context": {}
                    }
                ]
                
                # Both should implement the same interface
                custom_examples = await custom_synthesizer.generate_synthetic_dataset(workflow=mock_workflow, num_scenarios=1)
                deepeval_examples = await deepeval_synthesizer.generate_synthetic_dataset(num_scenarios=1)
                
                assert len(custom_examples) == 1
                assert len(deepeval_examples) == 1
                
                # Both should return SyntheticExample instances
                assert isinstance(custom_examples[0], SyntheticExample)
                assert isinstance(deepeval_examples[0], SyntheticExample)
                
    def test_persistence_compatibility(self, base_config):
        """Test that both synthesizers work with different persistence providers"""
        
        # Test with mock persistence
        mock_persistence = MockPersistence()
        
        custom_synthesizer = CustomSynthesizer(base_config, persistence=mock_persistence)
        deepeval_synthesizer = DeepEvalSynthesizer(base_config, persistence=mock_persistence)
        
        assert custom_synthesizer.persistence == mock_persistence
        assert deepeval_synthesizer.persistence == mock_persistence
        
        # Test with default LangSmith persistence
        custom_default = CustomSynthesizer(base_config)
        deepeval_default = DeepEvalSynthesizer(base_config)
        
        assert isinstance(custom_default.persistence, LangSmithPersistence)
        assert isinstance(deepeval_default.persistence, LangSmithPersistence)


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_scenario_generation_failure(self, base_config, mock_workflow, mock_persistence):
        """Test handling of scenario generation failures"""
        
        synthesizer = CustomSynthesizer(base_config, persistence=mock_persistence)
        
        # Mock scenario generation to return empty list
        with patch.object(synthesizer, 'generate_scenarios_from_workflow') as mock_scenarios:
            mock_scenarios.return_value = []
            
            examples = await synthesizer.generate_synthetic_dataset(workflow=mock_workflow, num_scenarios=1)
            
            assert len(examples) == 0
            
    @pytest.mark.asyncio
    async def test_workflow_execution_failure(self, base_config, mock_persistence):
        """Test handling of workflow execution failures"""
        
        # Create a failing workflow
        class FailingWorkflow:
            async def ainvoke(self, input_data, config=None):
                raise Exception("Workflow execution failed")
                
        failing_workflow = FailingWorkflow()
        synthesizer = CustomSynthesizer(base_config, mode=ExecutionMode.EXECUTION, persistence=mock_persistence)
        
        # Mock scenario generation
        with patch.object(synthesizer, 'generate_scenarios_from_workflow') as mock_scenarios:
            mock_scenarios.return_value = [
                {
                    "user_input": "Test input",
                    "expected_behavior": "Test behavior",
                    "complexity": "simple",
                    "target_agents": ["test_agent"],
                    "required_tools": ["test_tool"],
                    "context": {}
                }
            ]
            
            examples = await synthesizer.generate_synthetic_dataset(workflow=failing_workflow, num_scenarios=1)
            
            # Should handle failure gracefully
            assert len(examples) == 0 or examples[0].metadata.get("error") is not None


# Integration test that can be run manually
async def integration_test():
    """Integration test with real components (run manually)"""
    
    print("🧪 Running Integration Test")
    print("=" * 50)
    
    # Configuration
    config = SynthesizerConfig(
        project_name="integration-test",
        tags=["integration", "test"],
        trace_metadata={"environment": "test", "version": "1.0"},
        num_scenarios=2
    )
    
    # Test CustomSynthesizer in both modes
    print("\n🎭 Testing CustomSynthesizer - SYNTHETIC Mode")
    mock_workflow = MockWorkflow()
    
    custom_synthetic = CustomSynthesizer(config, mode=ExecutionMode.SYNTHETIC)
    
    # Mock scenario generation for integration test
    with patch.object(custom_synthetic, 'generate_scenarios_from_workflow') as mock_scenarios:
        mock_scenarios.return_value = [
            {
                "user_input": "What is 2+2?",
                "expected_behavior": "Calculate and return the result",
                "complexity": "simple",
                "target_agents": ["alice_agent"],
                "required_tools": ["calculate_math"],
                "context": {}
            }
        ]
        
        # Mock synthetic response generation
        with patch.object(custom_synthetic, '_generate_synthetic_response') as mock_response:
            mock_response.return_value = {"messages": [{"role": "assistant", "content": "2+2 equals 4"}]}
            
            synthetic_examples = await custom_synthetic.generate_synthetic_dataset(workflow=mock_workflow, num_scenarios=1)
            
            print(f"   ✅ Generated {len(synthetic_examples)} synthetic examples")
            if synthetic_examples:
                print(f"   📝 Sample input: {synthetic_examples[0].input_data}")
                print(f"   🎯 Sample output: {synthetic_examples[0].expected_output}")
    
    print("\n🚀 Testing CustomSynthesizer - EXECUTION Mode")
    custom_execution = CustomSynthesizer(config, mode=ExecutionMode.EXECUTION)
    
    # Test with mock workflow
    with patch.object(custom_execution, 'generate_scenarios_from_workflow') as mock_scenarios:
        mock_scenarios.return_value = [
            {
                "user_input": "What is 3+3?",
                "expected_behavior": "Calculate and return the result",
                "complexity": "simple",
                "target_agents": ["alice_agent"],
                "required_tools": ["calculate_math"],
                "context": {}
            }
        ]
        
        execution_examples = await custom_execution.generate_synthetic_dataset(workflow=mock_workflow, num_scenarios=1)
        
        print(f"   ✅ Generated {len(execution_examples)} execution examples")
        if execution_examples:
            print(f"   📝 Sample input: {execution_examples[0].input_data}")
            print(f"   🎯 Sample output: {execution_examples[0].expected_output}")
    
    print("\n🤖 Testing DeepEvalSynthesizer")
    deepeval_synthesizer = DeepEvalSynthesizer(config)
    
    # Mock DeepEval for integration test
    mock_deepeval = Mock()
    mock_deepeval.synthetic_goldens = [
        Mock(input="Test question", expected_output="Test answer")
    ]
    
    with patch('sample_agent.evaluations.datasets.generator.synthesizer.deepeval_synthesizer.Synthesizer') as mock_synthesizer_class:
        mock_synthesizer_class.return_value = mock_deepeval
        
        deepeval_examples = await deepeval_synthesizer.generate_synthetic_dataset(num_scenarios=1)
        
        print(f"   ✅ Generated {len(deepeval_examples)} DeepEval examples")
        if deepeval_examples:
            print(f"   📝 Sample input: {deepeval_examples[0].input_data}")
            print(f"   🎯 Sample output: {deepeval_examples[0].expected_output}")
    
    print("\n✅ Integration test completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    # Run integration test
    asyncio.run(integration_test()) 