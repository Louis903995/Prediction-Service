az identity create --name id-simplon-certif-acr-deployer --resource-group RG-SIMPLON-CERTIF
az role assignment create \
  --assignee 52b0c426-47ce-4d68-8536-1777224eba23 \
  --role AcrPush \
  --scope /subscriptions/de72360b-17c7-4771-9421-9ea5ed701ca2/resourceGroups/RG-SIMPLON-CERTIF/providers/Microsoft.ContainerRegistry/registries/crsimploncertif


az acr login --name crsimploncertif
docker push crsimploncertif.azurecr.io/prediction-service:0.1.2

az containerapp create \
    --name prediction-service \
    --resource-group RG-SIMPLON-CERTIF \
    --environment cae-simplon-certif \
    --image crsimploncertif.azurecr.io/prediction-service:0.1.2 \
    --target-port 80 \
    --ingress external \
    --registry-server crsimploncertif.azurecr.io \
    --user-assigned "id-simplon-certif-acr-deployer" \
    --registry-identity /subscriptions/de72360b-17c7-4771-9421-9ea5ed701ca2/resourcegroups/RG-SIMPLON-CERTIF/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id-simplon-certif-acr-deployer \
    --query properties.configuration.ingress.fqdn

az containerapp update \
  --name prediction-service \
  --resource-group RG-SIMPLON-CERTIF \
  --image crsimploncertif.azurecr.io/prediction-service:0.1.2    


