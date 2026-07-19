output "ack_cluster_id" {
  value = alicloud_cs_managed_kubernetes.ack.id
}

output "oss_bucket" {
  value = alicloud_oss_bucket.assets.bucket
}

output "acr_namespace" {
  value = alicloud_cr_ee_namespace.acr_namespace.name
}

output "kms_key_id" {
  value     = alicloud_kms_key.secrets.id
  sensitive = true
}
