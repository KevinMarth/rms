from flask import Flask, request
import json
import socket
import os

app = Flask(__name__)

@app.route('/v2/discovery:clusters', methods=['POST'])
def clusters():
    app.logger.info("Request Data %s", request.data)
    response = {
        "resources": [
            {
                "@type": "type.googleapis.com/envoy.api.v2.Cluster",
                "name": "service-1",
                "connect_timeout": "0.25s",
                "type": "STRICT_DNS",
                "lb_policy": "ROUND_ROBIN",
                "http2_protocol_options": {},
                "hosts": [
                    {
                        "socket_address": {
                            "address": "service-1",
                            "port_value": 80
                        }
                    }
                ]
            },
            {
                "@type": "type.googleapis.com/envoy.api.v2.Cluster",
                "name": "service-2",
                "connect_timeout": "0.25s",
                "type": "STRICT_DNS",
                "lb_policy": "ROUND_ROBIN",
                "http2_protocol_options": {},
                "hosts": [
                    {
                        "socket_address": {
                            "address": "service-2",
                            "port_value": 80
                        }
                    }
                ]
            }
        ]
    }
    return json.dumps(response)

@app.route('/v2/discovery:listeners', methods=['POST'])
def listeners():
    app.logger.info("Request Data %s", request.data)
    response = {
        "resources": [
            {
                "@type": "type.googleapis.com/envoy.api.v2.Listener",
                "address": {
                    "socket_address": {
                        "address": "0.0.0.0",
                        "port_value": 80
                    }
                },
                "filter_chains": [
                    {
                        "filters": [
                            {
                                "name": "envoy.http_connection_manager",
                                "config": {
                                    "codec_type": "AUTO",
                                    "stat_prefix": "ingress_http",
                                    "rds": {
                                        "route_config_name": "local_route",
                                        "config_source": {
                                            "api_config_source": {
                                                "api_type": "REST",
                                                "cluster_names": ["service-xds"],
                                                "refresh_delay": "1s"
                                            }
                                        }
                                    },
                                    "http_filters": [
                                        {
                                            "name": "envoy.router",
                                            "config": {}
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }
    return json.dumps(response)

@app.route('/v2/discovery:routes', methods=['POST'])
def routes():
    app.logger.info("Request Data %s", request.data)
    response = {
        "resources": [
            {
                "@type": "type.googleapis.com/envoy.api.v2.RouteConfiguration",
                "name": "local_route",
                "virtual_hosts": [
                    {
                        "name": "service-1",
                        "domains": ["service-1.useast2.rentpath.com"],
                        "routes": [
                            {
                                "match": {"path": "/service"},
                                "route": {
                                    "prefix_rewrite": "/service/hello",
                                    "cluster": "service-1"
                                }
                            },
                            {
                                "match": {"path": "/service/greet"},
                                "route": {
                                    "prefix_rewrite": "/service/hello",
                                    "cluster": "service-1"
                                }
                            },
                            {
                                "match": {"prefix": "/service"},
                                "route": {"cluster": "service-1"}
                            }
                        ]
                    },
                    {
                        "name": "service-2",
                        "domains": ["service-2.useast2.rentpath.com"],
                        "routes": [
                            {
                                "match": {"prefix": "/service"},
                                "route": {"cluster": "service-2"}
                            }
                        ]
                    }
                ]
            }
        ]}
    return json.dumps(response)

@app.route('/service/hello')
def hello():
    return ('    Hello from service-{}! [hostname: {}]\n'
            .format(os.environ['SERVICE'],
                    socket.gethostbyname(socket.gethostname())
            ))

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def default(path):
    return ('    Path /{} from service-{}? [hostname: {}]\n'
            .format(path,
                    os.environ['SERVICE'],
                    socket.gethostbyname(socket.gethostname())
            ))

if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=True)
