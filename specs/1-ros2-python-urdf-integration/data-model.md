# Data Model: ROS 2 Educational System

## Student Profile
- **student_id**: Unique identifier for each student
- **skill_level**: Enum (beginner, intermediate, advanced) indicating programming/robotics experience
- **preferred_learning_style**: Enum (visual, auditory, hands-on) for personalized content delivery
- **progress_tracking**: Collection of completed modules and assessments
- **hardware_access**: Enum (simulation_only, has_robot, cloud_access) indicating available resources

## Course Module
- **module_id**: Unique identifier for each educational module
- **title**: Name of the module (e.g., "ROS 2 Nodes", "Topics and Communication")
- **duration_hours**: Estimated time to complete the module
- **prerequisites**: List of module_ids that must be completed first
- **learning_objectives**: Collection of specific skills/knowledge to be acquired
- **content_type**: Enum (theory, practical, assessment) indicating the nature of the module

## Practical Exercise
- **exercise_id**: Unique identifier for each hands-on exercise
- **module_id**: Reference to the parent module
- **difficulty_level**: Enum (easy, medium, hard) for appropriate challenge level
- **required_resources**: List of ROS 2 packages, simulation environments, or hardware needed
- **code_templates**: Starter code for students to build upon
- **expected_outcomes**: Specific behaviors or results students should achieve

## Assessment
- **assessment_id**: Unique identifier for each evaluation
- **type**: Enum (quiz, practical_project, peer_review) indicating assessment method
- **module_id**: Reference to the associated module
- **passing_criteria**: Minimum score or requirements for successful completion
- **attempts_allowed**: Number of times a student can attempt the assessment
- **feedback_mechanism**: How and when feedback is provided to students

## Code Example
- **example_id**: Unique identifier for each code sample
- **module_id**: Reference to the associated module
- **language**: Programming language (typically Python for rclpy examples)
- **complexity**: Enum (basic, intermediate, advanced) indicating difficulty
- **purpose**: Description of what concept the example demonstrates
- **dependencies**: List of ROS 2 packages or message types required
- **runnable**: Boolean indicating if the example can be executed in the learning environment

## Learning Resource
- **resource_id**: Unique identifier for each educational resource
- **title**: Descriptive name for the resource
- **type**: Enum (video, document, interactive, simulation) indicating resource format
- **url**: Location of the resource (file path or web URL)
- **estimated_time**: Time needed to consume the resource
- **associated_module**: Module this resource supports
- **difficulty**: Enum (introductory, intermediate, advanced) matching student levels