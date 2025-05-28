export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface SubTask {
  description: string;
  estimated_time: string;
  dependencies: string[];
}

export interface TaskAnalysis {
  main_goal: string;
  complexity: string;
  subtasks: SubTask[];
  potential_risks: string[];
  required_resources: string[];
  estimated_total_time: string;
}

export interface Action {
  action_type: string;
  description: string;
  parameters: Record<string, any>;
  status: string;
  subtask_id: string;
}

export interface Plan {
  goal: string;
  analysis: TaskAnalysis;
  actions: Action[];
  status: string;
}

export interface ChatResponse {
  messages: Message[];
  needs_clarification: boolean;
  clarification_questions?: string[];
  concerns?: string[];
  current_plan?: Plan;
  finished: boolean;
}
