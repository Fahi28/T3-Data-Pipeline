provider "aws" {
  region = "eu-west-2"
}

data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"  
}

data "aws_iam_role" "ecs_task_role" {
    name="ecsTaskExecutionRole"
}


resource "aws_ecs_task_definition" "c14-fahad_task_definition-2" {
  family                   = "c14-fahad-task-definition-2"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]  
  cpu                      = "256" 
  memory                   = "1024"  

  runtime_platform {
    operating_system_family = "LINUX"   
    cpu_architecture        = "X86_64"  
  }

  execution_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "c14-fahad-container"
      image     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c14-fahad-ecr-2:latest" 
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
        },
        {
          containerPort = 8501
          hostPort = 8501
          protocol = "tcp"
          name = "streamlit"
          
        }
      ]
      environment = [
        {
          name  = "DB_HOST"
          value = var.DB_HOST
        },
        {
          name  = "DB_PORT"
          value = var.DB_PORT
        },
        {
          name  = "DB_NAME"
          value = var.DB_NAME
        },
        {
          name  = "DB_USERNAME"
          value = var.DB_USERNAME
        },
        {
          name  = "DB_PASSWORD"
          value = var.DB_PASSWORD
        },
        {
          name  = "DB_SCHEMA"
          value = var.DB_SCHEMA
        },
        {
          name  = "AWS_ACCESS_KEY_ID"
          value = var.AWS_ACCESS_KEY_ID
        },
        {
          name  = "AWS_SECRET_ACCESS_KEY"
          value = var.AWS_SECRET_ACCESS_KEY
        },
        {
          name  = "BUCKET_NAME"
          value = var.BUCKET_NAME
        }
          
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-create-group"  = "true"
          "awslogs-group"         = "/ecs/c14-fahad-task-definition-2"
          "awslogs-region"        = "eu-west-2"
          "awslogs-stream-prefix" = "ecs"
          "max-buffer-size"       = "25m"
          "mode"                  = "non-blocking"
        }
      }
    }
  ])
}