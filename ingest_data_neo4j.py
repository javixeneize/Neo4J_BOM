from neo4j import GraphDatabase
import get_dc_data
import os
import click


def ingest_project(project):
    tx.run('''
    MERGE (n:project {project_name: $project})
    ''', project=project)


def ingest_vulns(vulns_list):
    tx.run('''    UNWIND $mapEntry AS mItem
              CALL apoc.merge.node(["vulnerability"],
              {vulnerability_name:mItem["CVE"],
              severity:mItem["CVSSv3"]})
              YIELD node
              return node
            '''
           , mapEntry=vulns_list)


def ingest_dependencies(dependencies, project):
    for dependency in dependencies:
        r = tx.run('''
          MATCH (d:dependency {dependency: $dependency})
          return d
                 ''', dependency=dependency.get('dependency'))
        if r.single():
            tx.run('''
          MATCH (d:dependency {dependency: $dependency})
          WHERE NOT ($projects  IN d.projects)
          SET d.projects = d.projects + $projects
                 ''',
                   dependency=dependency.get('dependency'), projects=project)

            tx.run('''
          MATCH (d:dependency {dependency: $dependency})
          SET d.vulnerabilities = $vulnerabilities
          ''',
                   dependency=dependency.get('dependency'), vulnerabilities=dependency.get('vulnerabilities'))

        else:
            tx.run('''
            MERGE (d:dependency {package: $package, dependency: $dependency,
            vulnerabilities: $vulnerabilities, projects: $projects})
            ''', package=dependency.get('package'), dependency=dependency.get('dependency'),
                   vulnerabilities=dependency.get('vulnerabilities'), projects=dependency.get('project'))


def create_vuln_relations():
    tx.run('''   MATCH (d:dependency), (v:vulnerability)
    WHERE v.vulnerability_name IN  d.vulnerabilities

    MERGE(d)-[:VULNERABLE_TO]->(v)
    ''')


def create_project_relations():
    r = tx.run('''
    MATCH (d:dependency), (p:project)
    WHERE p.project_name IN  d.projects
    MERGE (p)-[:USES]->(d)
    ''')


@click.command()
@click.argument('project', required=True)
@click.argument('file', required=False)
def run_cli_scan(project, file):
    if not file:
        file = 'dependency-check-report.json'
    project = project
    deps, vulns = get_dc_data.get_depcheck_data(project, file)
    if deps:
        ingest_project(project)
        ingest_dependencies(deps, project)
        ingest_vulns(vulns)
        create_vuln_relations()
        create_project_relations()
        print("Data successfully ingested in Neo4J")
    else:
        print("No data has been ingested")


if __name__ == "__main__":
    driver = GraphDatabase.driver(os.environ.get('NEO4J_DB'),
                                  auth=(os.environ.get('NEO4J_USER'), os.environ.get('NEO4J_PWD')))
    tx = driver.session()
    run_cli_scan()
    driver.close()
