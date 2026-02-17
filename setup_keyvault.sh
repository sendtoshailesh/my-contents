#!/bin/bash

# Azure Key Vault Setup Script

SUBSCRIPTION_ID="17107fe3-5d6d-4cfb-940a-8eeb0e651e2e"
RESOURCE_GROUP="rg-content-studio"
LOCATION="eastus"
KEY_VAULT_NAME="kv-content-studio-$(date +%s | tail -c 8)"
BING_SEARCH_KEY="36f800cdc9064f74a39fe86942b660d4"

echo "📋 Configuration:"
echo "  Subscription ID: $SUBSCRIPTION_ID"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Key Vault Name: $KEY_VAULT_NAME"
echo ""

echo "🔐 Step 1: Set active subscription..."
az account set --subscription "$SUBSCRIPTION_ID"
echo "✅ Subscription set"
echo ""

echo "📦 Step 2: Create resource group..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
echo "✅ Resource group created"
echo ""

echo "🔓 Step 3: Create Key Vault..."
az keyvault create \
   --resource-group "$RESOURCE_GROUP" \
   --name "$KEY_VAULT_NAME" \
   --location "$LOCATION"
echo "✅ Key Vault created"
echo ""

echo "👤 Step 4: Grant yourself access..."
az keyvault set-policy \
   --name "$KEY_VAULT_NAME" \
   --upn "$(az account show --query user.name -o tsv)" \
   --secret-permissions get list set delete
echo "✅ Access granted"
echo ""

echo "🔑 Step 5: Store Bing Search key..."
az keyvault secret set --vault-name "$KEY_VAULT_NAME" \
   --name "bing-search-key" --value "$BING_SEARCH_KEY"
echo "✅ Bing Search key stored"
echo ""

echo "🎉 KEY VAULT SETUP COMPLETE!"
echo ""
echo "📌 Save this for later:"
echo "   Key Vault Name: $KEY_VAULT_NAME"
echo ""
echo "You can now use this Key Vault as a fallback for your secrets."
