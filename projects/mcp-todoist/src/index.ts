import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { TodoistApi } from "@doist/todoist-api-typescript";

const API_TOKEN = process.env.TODOIST_API_TOKEN;
if (!API_TOKEN) throw new Error("TODOIST_API_TOKEN env var is required");

const api = new TodoistApi(API_TOKEN);

const server = new Server(
  { name: "mcp-todoist", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "get_tasks",
      description: "Get all active tasks, optionally filtered by project",
      inputSchema: {
        type: "object",
        properties: {
          project_id: { type: "string", description: "Filter by project ID (optional)" },
        },
      },
    },
    {
      name: "create_task",
      description: "Create a new task",
      inputSchema: {
        type: "object",
        properties: {
          content: { type: "string", description: "Task title" },
          description: { type: "string", description: "Task description (optional)" },
          due_string: { type: "string", description: "Due date in natural language, e.g. 'tomorrow', 'next monday'" },
          priority: { type: "number", description: "Priority 1-4 (4=urgent)", minimum: 1, maximum: 4 },
          project_id: { type: "string", description: "Project ID (optional)" },
        },
        required: ["content"],
      },
    },
    {
      name: "complete_task",
      description: "Mark a task as complete",
      inputSchema: {
        type: "object",
        properties: {
          task_id: { type: "string", description: "Task ID to complete" },
        },
        required: ["task_id"],
      },
    },
    {
      name: "get_projects",
      description: "List all projects",
      inputSchema: { type: "object", properties: {} },
    },
    {
      name: "delete_task",
      description: "Delete a task",
      inputSchema: {
        type: "object",
        properties: {
          task_id: { type: "string", description: "Task ID to delete" },
        },
        required: ["task_id"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "get_tasks": {
        const tasks = await api.getTasks(args?.project_id ? { projectId: args.project_id as string } : undefined);
        return {
          content: [{ type: "text", text: JSON.stringify(tasks, null, 2) }],
        };
      }
      case "create_task": {
        const task = await api.addTask({
          content: args!.content as string,
          description: args?.description as string | undefined,
          dueString: args?.due_string as string | undefined,
          priority: args?.priority as number | undefined,
          projectId: args?.project_id as string | undefined,
        });
        return {
          content: [{ type: "text", text: `Created task: ${task.id} — ${task.content}` }],
        };
      }
      case "complete_task": {
        await api.closeTask(args!.task_id as string);
        return {
          content: [{ type: "text", text: `Task ${args!.task_id} completed.` }],
        };
      }
      case "get_projects": {
        const projects = await api.getProjects();
        return {
          content: [{ type: "text", text: JSON.stringify(projects, null, 2) }],
        };
      }
      case "delete_task": {
        await api.deleteTask(args!.task_id as string);
        return {
          content: [{ type: "text", text: `Task ${args!.task_id} deleted.` }],
        };
      }
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (err) {
    return {
      content: [{ type: "text", text: `Error: ${(err as Error).message}` }],
      isError: true,
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
