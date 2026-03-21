data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_instance" "k3s_node" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = var.key_name != "" ? var.key_name : null

  subnet_id                   = aws_subnet.k3s_subnet_public.id
  vpc_security_group_ids      = [aws_security_group.k3s_sg.id]
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.k3s_ec2_profile.name

  user_data = file("${path.module}/user_data.sh")

  root_block_device {
    volume_size = 20 # Free tier includes up to 30GB EBS
    volume_type = "gp3"
  }

  tags = {
    Name = "k3s-single-node"
  }
}
