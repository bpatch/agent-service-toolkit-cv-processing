from .agent.graph import CVAgent


def process_cv():

    config = {}  # Placeholder for config to pass to graph, nodes, and edges

    cv_agent = CVAgent(config)

    cv_agent_response = cv_agent.agent.invoke(
        {
            "doc_id": "123abc",
        }
    )

    print(f"{cv_agent_response=}")


if __name__ == "__main__":
    process_cv()
