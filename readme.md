### Intro

This project loads the report from dependency check into Neo4J to do a visualisation of the dependencies and vulnerabilities in a nice format using a graph database.



### How does it work?

The project needs a dependency check report previously generated. The generation of this report is not part of this project, refer to [Dependency Check official website](https://jeremylong.github.io/DependencyCheck/) for information about how to generate this. A sample of this report is included in the project for testing purposes.

The tool requires the Neo4J username, password and database configured as environmental variables:

`NEO4J_USER=MYUSER
NEO4J_PWD=MYPASSWORD
NEO4J_DB=bolt://Neo4J_Location:port`



It also requires the name of the project to install and optionally the path to the dependency check JSON report. If this parameter is not set, it defaults to *dependency-check-report.json*. So, the command to run it would be:

`python ingest_data_neo4j.py testjavi myreport.json`



### Code explained

### Visualisations

![](/Users/javidr/javi/python/Neo4J_BOM/images/neo4j_display.png)

### Next steps

There are some improvements on the road:

- [ ] Integrate dependency check scan
- [ ] Add second level dependencies and its relationship with the parent one