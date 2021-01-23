<h1 align="center"> fastapi-blockchain-template</h1>

<p align="center">Cloud-native Blockchain Network Implementation in Python with <b>FastAPI</b>, Docker, Kubernetes and Okteto Cloud.</p>
<p align="center">
<img src="https://www.nicepng.com/png/detail/67-670388_the-blockchain-is-a-decentralized-technology-that-it.png" width="25%" />
</p>


## Dependencies and Tools 
pip packages: 
- fastapi
- httpx 
- gunicorn 
- uvicorn 
- pif 
- pydantic 
- python-dotenv 

dev: 
- Okteto 
- Docker 

deployment: 
- Heroku
- Kubernetes


## Documentation 

- Blockchain Server: [http://{ip_address}:{port}/docs]() 
- Node Application: [http://{ip_address}:{port}/node/docs]()


## Development 

<b>Local:</b> 
```
$ git clone https://github.com/codeamt/fastapi-blockchain-template.git
$ cd fastapi-blockchain-template
$ sh run.sh 
```

<b>Docker (Build):</b> 
```
$ docker build -f Dockerfile -t app:latest ./code
```

<b> Docker (Run):</b><br>
Add a ```.env``` file to your root and: 
```
$ docker run -p 5000:5000 --env-file=env_file_name app:latest
```

<b>Okteto:</b>
```
$ okteto login 
$ okteto namespace
$ okteto init --deploy
```

## Production 

<b>Heroku:</b> 

Install [Heroku CLI tools](), then from the root:
```
$ git init
$ touch .gitignore 
$ echo ".env" >> .gitignore
$ git add . 
$ git commit -m "deploying to heroku"
$ heroku login
$ heroku create <optional: app_name>
$ heroku config:set PORT=<desired_port>
$ heroku config:set BLOCKCHAIN_URL=http://127.0.0.1:{PORT}
$ heroku config:set INITIAL_DIFFICULTY=2
$ git push heroku main
$ heroku open 
```

<b>Kubernetes Cluster:</b> 
```
$ kubectl apply -f k8s.yml
```


## Endpoints 

<b>Blockchain Server:</b> 

<table style="align: left; width:100%">
<th>
  <b style="text-align:center">Endpoint</b>
</th>
<th>
  <b style="text-align:center">Description</b>
</th>
<tr>
  <td>
   <b><code>/</code></b>
  </td>
  <td>
      Index endpoint for Blockchain server.<br>
    :return: str
  </td>
</tr>
 
 <tr>
  <td>
   <b><code>/mainchain</code></b>
  </td>
  <td>
    Ledger endpoint for Blockchain server.<br>
    :return: dict -> keys: peers: List[str]
  </td>
</tr>

<tr>
  <td>
   <b><code>/peers</code></b>
  </td>
  <td>
   Peers List endpoint for Blockchain Server.<br>
   :return: dict -> keys: chain:Lis[dict] -> Serialized Blocks
  </td>
</tr>

<tr>
  <td>
   <b><code>/new-peer</code><b>
  </td>
  <td>
   Endpoint for creating new peer.<br>
   :param request: Request<br>
    :return: dict -> keys: new_peer:str -> IP Address
  </td>
</tr>

<tr>
  <td>
   <b><code>/new_tx</code></b>
  </td>
  <td>
   New Transaction endpoint for Blockchain Server.<br>
    :param request: Request -> HTTP POST request.<br>
    :return: dict -> keys: sender:str; receipt:dict
  </td>
</tr>

<tr>
  <td>
   <b><code>/mempool</code></b>
  </td>
  <td>
   Mempool endpoint for Blockchain Server.<br>
    :return: dict -> keys: mempool:dict
  </td>
</tr>

<tr>
  <td>
   <b><code>/new_block</code></b>
  </td>
  <td>
   ew Block endpoint for Blockchain Server.<br>
    :param request: Request -> HTTP POST request.<br>
    :return: dict -> keys: miner_address:str, latest_block:dict, new_chain:List[dict]
  </td>
</tr>
</table>




<b>Bootstrap Node Application:</b>


<table style="align: left; width: 500px">
<th>
  <b style="text-align:center">Endpoint</b>
</th>
<th>
  <b style="text-align:center">Description</b>
</th>
<tr>
  <td style="width:25%;">
   <b><code>/node</code></b>
  </td>
  <td>
   Index endpoint for Bootstrap Node Client.<br>
   :return: dict: keys: local_chain: List[dict] -> Local chain.
  </td>
</tr>
 
 <tr>
  <td>
   <b><code>/chain</code></b>
  </td>
  <td>
   Consensus Endpoint for BootStrap Node App.<br>
   :return: dict: keys: local_chain: List[dict]
  </td>
</tr>

<tr>
  <td>
   <b><code>/peer-nodes</code></b>
  </td>
  <td>
   Network Peers List Endpoint for Bootstrap Node App.<br>
   :return: dict: List[str]
  </td>
</tr>

<tr>
  <td>
   <b><code>/mine</code></b>
  </td>
  <td>
   Mining Endpoint for Bootstrap Node App.<br>
   :return: dict: block:dict -> New Block (serialized)
  </td>
</tr>

<tr>
  <td>
   <b><code>/transact</code></b>
  </td>
  <td>
   New Transaction Endpoint for Bootstrap Node App.<br>
   :return: dict: keys: sender:str; receipt:dict
  </td>
</tr>

<tr>
  <td>
   <b><code>/mem_pool</code></b>
  </td>
  <td>
   Mempool Endpoint for Bootstrap Node App.<br>
   :return: dict: keys: mempool:dict -> Mempool State.
  </td>
</tr>
</table>


**TODO:** 
- Configure Postgres DB
- Reactive Frontend Application for Bootstrap Node
- Unit Tests 


