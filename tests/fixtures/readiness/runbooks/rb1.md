# Queue backlog
## Symptoms
Queue depth alert fires above 10,000 messages.
## Impact check
1. Run `az servicebus queue show -n orders -g $RG --namespace-name $NS --subscription $SUB --query countDetails`; expect activeMessageCount.
## Diagnosis
1. Run `az monitor metrics list --resource $WORKER_ID --metric CpuPercentage --subscription $SUB`; expect CPU under 80.
## Mitigation
1. Scale workers: `az containerapp update -n worker -g $RG --min-replicas 6 --subscription $SUB`; expect provisioningState Succeeded.
## Verification
1. Re-run the impact check; expect the count to fall within 15 minutes.
## Rollback
1. Restore replicas: `az containerapp update -n worker -g $RG --min-replicas 2 --subscription $SUB`; expect provisioningState Succeeded.
## Escalation
Page the orders on-call if the count keeps rising after 15 minutes.
