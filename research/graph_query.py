from neo4j import GraphDatabase

def get_neo4j_connection():
    """Establish connection to Neo4j database"""
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "ttt@123ASD"
    
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        return driver
    except Exception as e:
        print(f"Error connecting to Neo4j: {e}")
        return None

def get_all_nodes():
    """Retrieve all nodes from the Neo4j database"""
    driver = get_neo4j_connection()
    if not driver:
        return []
    
    try:
        with driver.session() as session:
            # Cypher query to get all nodes
            query = "MATCH (n) RETURN n"
            result = session.run(query)
            
            # Convert results to list of nodes
            nodes = [record["n"] for record in result]
            return nodes
            
    except Exception as e:
        print(f"Error querying nodes: {e}")
        return []
    finally:
        driver.close()


# Example usage
nodes = get_all_nodes()
for node in nodes:
    print(f"Node: {node}")

def truncate_all_nodes():
    """Delete all nodes and relationships from the Neo4j database"""
    driver = get_neo4j_connection()
    if not driver:
        return
    
    try:
        with driver.session() as session:
            query = "MATCH (n) DETACH DELETE n"
            session.run(query)
            print("Successfully deleted all nodes and relationships")
            
    except Exception as e:
        print(f"Error truncating database: {e}")
    finally:
        driver.close()

# Execute truncate
truncate_all_nodes()