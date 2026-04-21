import asyncio

from TARS.agent.tools.shell import ExecTool


async def main():
    tool = ExecTool(workspace_dir="/tmp/workspace", restrict_to_workspace=True)
    print(tool._guard_command("cd .. && cat /etc/passwd", "/tmp/workspace"))
    print(tool._guard_command("cd ..; cat /etc/passwd", "/tmp/workspace"))
    print(tool._guard_command("cd ..| cat /etc/passwd", "/tmp/workspace"))
    print(tool._guard_command("cd ../ && cat /etc/passwd", "/tmp/workspace"))
    print(tool._guard_command("cat foo..bar", "/tmp/workspace"))


if __name__ == "__main__":
    asyncio.run(main())
