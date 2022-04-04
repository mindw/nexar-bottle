import sys
from index import Index
import bottle
from bottle import route, run, template, request
from prometheus_client import make_wsgi_app, Histogram

app = bottle.Bottle()
app.mount("/metrics", make_wsgi_app())


if __name__ == '__main__':
    index = Index.new(sys.argv[1])

    REQUEST_TIME = Histogram('response_latency_seconds', 'Response latency (seconds)')

    @app.route('/')
    @REQUEST_TIME.time()
    def search():
        q = request.query.q
        print(q, type(q))
        return dict(results=list(index.search(str(q))))

    @app.route('/healthz')
    def health():
        return bottle.HTTPResponse(status=200)

    @app.route('/readyz')
    def ready():
        return bottle.HTTPResponse(status=200)

    run(app=app, host="0.0.0.0", debug=True)
