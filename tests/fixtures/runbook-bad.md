# Queue backlog
## Symptoms
Queue depth alert.
## Diagnosis
1. Check the logs.
## Mitigation
1. Delete the stuck consumer group: `az servicebus topic subscription delete -n sub1 -g rg-prod --namespace-name ns1`
2. Run `sudo systemctl restart worker`
