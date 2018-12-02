status:
	docker-compose ps && docker ps -a && docker image ls

build:
	docker-compose build --force-rm

start: rotor-static.yaml
	docker-compose up --detach

stop:
	docker-compose stop

down:
	docker-compose down

test: test-1 test-2

test-1:
	@echo ====
	$(call test,1,8000)
	$(call test,1,8100)
	$(call test,1,8200)
	$(call test,1,9000)
	@echo ====

test-2:
	@echo ====
	$(call test,2,8000)
	$(call test,2,8100)
	$(call test,2,8200)
	$(call test,2,9000)
	@echo ====

clean:
	docker image prune --all --force
	rm -f rotor-static.yaml

restart: rotor-static.yaml
	docker-compose restart rotor

rotor-static.yaml: envoy-static.yaml
	sed -e '/^static_resources:$$/ d' -e '/^admin:$$/,$$ d' $< > $@

header-host = --header 'Host:service-$1.useast2.rentpath.com'

test = \
curl $(call header-host,$1) localhost:$2/service; \
curl $(call header-host,$1) localhost:$2/service/greet; \
curl $(call header-host,$1) localhost:$2/service/hello;
