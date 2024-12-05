def appName = 'github-project'

def createEnv() {
    sh 'echo "Creating environment"'
    sh 'python3 -m venv .venv'
    sh 'chmod +x .venv/bin/activate'
    sh '. .venv/bin/activate && pip install -r requirements.txt'
}

def deleteEnv() {
    sh 'echo "Deleting environment"'
    sh 'rm -rf .venv'
}

def loginToDockerHub() {
    sh "echo ${DOCKER_HUB_PASSWORD} | docker login -u ${DOCKER_HUB_USERNAME} --password-stdin"
}

def buildAndPushToDockerHub() {
    sh "docker build -t ${IMAGE_NAME}:latest ."
    sh "docker push ${IMAGE_NAME}:latest"
}

def cleanup() {
    sh 'docker volume prune -f && docker system prune -f'
}

pipeline {
    agent any

    environment {
        DOCKER_HUB_USERNAME = credentials('DOCKER_HUB_USERNAME')
        DOCKER_HUB_PASSWORD = credentials('DOCKER_HUB_PASSWORD')
        APP_NAME = 'docker-app'
        IMAGE_NAME = 'mawulib/docker-app'
    }

    stages {
        stage('VCSCheckout') {
            steps {
                git url: 'https://github.com/MawuliB/docker-app.git', branch: 'main'
                sh 'ls -l'
            }
        }

        stage('Test') {
            steps {
                sh '. .venv/bin/activate && flake8 main.py'
            }
        }

        stage('Build') {
            steps {
                loginToDockerHub()
                buildAndPushToDockerHub()
            }
        }

        stage('Deployment') {
            steps {
                sshagent(['ec2-ssh-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ubuntu@44.204.192.188 "docker pull ${IMAGE_NAME}:latest && docker run -d -p 5000:5000 ${IMAGE_NAME}:latest"
                    '''
                }
            }
        }

        stage('Cleanup') {
            steps {
                deleteEnv()
                cleanup()
            }
        }
    }

    post {
        always {
            sh 'echo "Pipeline completed"'
            cleanup()
        }
        success {
            sh 'echo "Pipeline completed successfully"'
        }
        failure {
            sh 'echo "Pipeline completed with errors"'
        }
    }
}