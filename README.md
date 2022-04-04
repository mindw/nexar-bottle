# Code assignment: document search

This assignment walks through a process of turning a simple Python application into a more production-ready app.

The task list may be long, so if there's anything you're struggling with, you're welcome to skip ahead. We don't need you to check items on a shopping list of tech skills, rather we want to focus on _how_ you work on the things you're already familiar with.

## Getting started

This assignment makes use of VS Code's remote development features, so that your development environment requires no toil to set up, and is consistent regardless of operating system or other dependencies.

### System Requirements

You need only two components:
1. A container runtime like Docker Desktop
2. Visual Studio Code

### Starting the development environment

1. Using Nexar's repository as a template, [create a new repository under your own Github account](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template#creating-a-repository-from-a-template), then clone that repo into a local directory, e.g. `$HOME/nexar-assignment`.
    Using the [GitHub CLI](https://cli.github.com/manual/gh_repo_create) you can do this with a single command:
    ```bash
    cd $HOME
    gh repo create \
       nexar-assignment \
       --template https://github.com/getnexar/infra-eng-assignment.git \
       --private # optional \
       --confirm # optional
    ```

2. Open your working copy in VS Code (e.g. `code $HOME/nexar-assignment` in macOS). A prompt should pop up asking you to open the directory in a container. Click 'Yes', let it build the dev container (takes 1-3 minutes), and once it's done, you're good to go.

## Background

The `doc-search` application implements a simple search endpoint over a set of documents. More specifically, given a dataset of documents, where each document has a numeric identifier, the endpoint returns a list of all of the document IDs containing ALL words in the `q` query parameter.

For example, if the web server is serving at http://localhost:8080, and the words `hello` and `world` both exist only in document 1, then the command `curl http://localhost:8080/?q=hello+world` should return:

```json
{
    "results": ["1"]
}
```

### Sanity checks

1. Run unit tests `cd doc-search/src/ && python -m unittest -b test_index`
2. Build the container image: `docker build . -t doc-search`
3. Run the app: `docker run -p 8080:8080 doc-search`.
**GabiD - broken app, defaults to serve on 127.0.0.1**<br>
4. Test the app: you can use `curl` to query it, for example: 
`curl http://localhost:8080/?q=hello+world` will return a JSON document with all the
documents containing both `hello` and `world`.

## Tasks

### Part 1: Improving the build

The app currently has a `Dockerfile` included under `doc-search/`.

1. Every commit to application code (`.py` files) results in a slow build of the container image. Modify the `Dockerfile` to make the build faster.
**GabiD - move app copy command to be last to utilize the docker cache**<br>
2. How can you minimize the size of the resulting container image? Modify the `Dockerfile` or describe your solution.
**GabiD - switch to alpine, disable generation of .pyc files during build down to ~50Mib vs 130Mib**<br>

**GabiD - using Visual Studio Code is time-consuming and error-prone, switched to a real IDE - PyCharm**<br>
**GabiD - TODO: add Makefile**<br>

### Part 2: Deploying to Kubernetes

Here you will deploy the application to a local Minikube.

1. Implement a minimal Helm chart for this application.
**GabiD - used manifests for development. Otherwise, would have used 
`helm create doc-search` to create a skeleton and populate it with the service and deployment**<br>
2. Deploy the chart to Minikube, under the `default` namespace.
**GabiD - done - `minikube create`, `minikube image load --daemon doc-search-alpine:latest`.
used latest to keep things simple.**<br>
3. Verify that you can call the service from outside the cluster.
**GabiD - use NodePort for simplicity - `minikube service --utl doc-search`**<br>
4. We want Kubernetes to tolerate a slow start for our app. Implement this behavior in your chart. Bonus points if you can simulate a slow start and test your solution.

**GabiD - unclear. Probes are implemented in the service. Possible ways to simulate this:**
1. insert a delay in the code (not so good)
2. modifying the command line of the container and inject a sleep. requires prior
knowledge of the container entrypoint/cmd:
```yaml
          command:
          - sh
          - -exc
          - >
            sleep 1m;
            python3 __init__.py /data
```

### Part 3: Observability

1. In the app's Python code, instrument latency of the `search/` endpoint, and expose a metrics HTTP endpoint on port `8000`. You may use any open-source library for this purpose.
**GabiD - programs doesn't have a `/search` endpoint**<br>
**GabiD - It seems to be very hard to expose the same app on two ports using WSGI and bottle - seems out of scope**
2. Add code and/or configuration that installs Prometheus onto the k8s cluster and configures it to scrape metrics from the app. **
**GabiD - added plain manifests to deploy prometheus and expose using node-port**<br>
3. Using a load generator like [`hey`](https://github.com/rakyll/hey), generate some load on the app.
4. Using the built-in web UI for Prometheus, chart the p50, p90, p99 latencies of `search/` requests over the load you generated before.
**GabiD:**
```
histogram_quantile(0.50, sum(rate(response_latency_seconds_bucket[10m])) by (le))
histogram_quantile(0.90, sum(rate(response_latency_seconds_bucket[10m])) by (le))
histogram_quantile(0.99, sum(rate(response_latency_seconds_bucket[10m])) by (le))
```
```shell
PROM_URL=$(minikube service --url prometheus -n kube-system)
python -m webbrowser -t '${PROM_URL}/graph?g0.expr=histogram_quantile(0.50%2C%20sum(rate(response_latency_seconds_bucket%5B10m%5D))%20by%20(le))&g0.tab=0&g0.stacked=0&g0.show_exemplars=0&g0.range_input=1h&g1.expr=histogram_quantile(0.90%2C%20sum(rate(response_latency_seconds_bucket%5B10m%5D))%20by%20(le))&g1.tab=0&g1.stacked=0&g1.show_exemplars=0&g1.range_input=1h&g2.expr=histogram_quantile(0.99%2C%20sum(rate(response_latency_seconds_bucket%5B10m%5D))%20by%20(le))&g2.tab=0&g2.stacked=0&g2.show_exemplars=0&g2.range_input=1h''
```
6. (Bonus) which other key metrics are important/useful to instrument in a web service like this? Add them as you see fit and show how you can query them in Prometheus.
**GabiD - Error rates, saturation. See USE method. Resource usages - CPU, memory, network**<br>
---

Good luck!
**GabiD - luck has nothing to do with it, rather it's the time available :)**<br>
