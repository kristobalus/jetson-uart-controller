```bash
docker image build -f ./Dockerfile -t testimg .
```

```bash
docker container run -it --rm \
--runtime=nvidia --gpus all \
--privileged \
--device /dev/ttyTHS0 \
--device /dev/ttyTHS1 \
--device /dev/ttyTHS4 \
-v ./:/opt \
testimg /bin/bash
```