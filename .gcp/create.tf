provider "google" {
  credentials = "${file("credentials.json")}"
  project     = "proarc-451622"
  region      = "us-central1-a"
}

module "firewall_rules" {
  source       = "terraform-google-modules/network/google//modules/firewall-rules"
  project_id   = "proarc-451622"
  network_name = "default"

  rules = [{
    name                    = "all-rules-ingress"
    description             = null
    direction               = "INGRESS"
    priority                = 1000
    source_ranges           = ["0.0.0.0/0"]
    source_tags             = null
    source_service_accounts = null
    target_tags             = null
    target_service_accounts = null
    allow = [{
      protocol = "tcp"
      ports    = ["22", "9999", "6666", "5432"]
    }]
    deny = []
  }]
}

resource "google_compute_instance" "default" {
  name         = "my-vm-01"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "ubuntu-minimal-2210-kinetic-amd64-v20230126"
    }
  }

  metadata = {
    startup-script = <<SCRIPT
    ${file("docker-script-build.tpl")}
    ${file("docker-compose-build.tpl")}
    ${file("execute-shell.tpl")}
    SCRIPT
  }

  network_interface {
    network = "default"
    access_config {}
  }
}