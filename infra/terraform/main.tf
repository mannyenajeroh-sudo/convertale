locals {
  name = "${var.name_prefix}-${var.environment}"
}

resource "alicloud_vpc" "main" {
  vpc_name   = local.name
  cidr_block = "10.42.0.0/16"
}

resource "alicloud_vswitch" "main" {
  vpc_id       = alicloud_vpc.main.id
  cidr_block   = "10.42.1.0/24"
  zone_id      = var.availability_zone
  vswitch_name = local.name
}

resource "alicloud_cs_managed_kubernetes" "ack" {
  name                 = local.name
  cluster_spec         = "ack.pro.small"
  version              = var.kubernetes_version
  worker_vswitch_ids   = [alicloud_vswitch.main.id]
  new_nat_gateway      = true
  slb_internet_enabled = true
}

resource "alicloud_cs_kubernetes_node_pool" "default" {
  cluster_id            = alicloud_cs_managed_kubernetes.ack.id
  node_pool_name        = "${local.name}-default"
  vswitch_ids           = [alicloud_vswitch.main.id]
  instance_types        = [var.worker_instance_type]
  system_disk_category  = "cloud_essd"
  system_disk_size      = 80
  password              = var.worker_password
  desired_size          = 2
  install_cloud_monitor = true
}

resource "alicloud_oss_bucket" "assets" {
  bucket = "${local.name}-assets"
  acl    = "private"
}

resource "alicloud_cr_ee_namespace" "acr_namespace" {
  name               = var.name_prefix
  auto_create        = true
  default_visibility = "PRIVATE"
}

resource "alicloud_kms_key" "secrets" {
  description            = "Showrunner ${var.environment} application secrets"
  deletion_window_in_days = 7
  status                 = "Enabled"
}
