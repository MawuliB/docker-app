def appName = 'github-project'

def imageName = 'mawulib/docker-app'

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
    sh 'docker login -u $DOCKER_HUB_USERNAME -p $DOCKER_HUB_PASSWORD'
}

def buildAndPushToDockerHub() {
    sh "docker build -t ${imageName}:latest ."
    sh "docker push ${imageName}:latest"
}

def cleanup() {
    sh 'docker volume prune -f && docker system prune -f'
}

pipeline {
    agent any
    stages {
        stage('VCSCheckout') {
            steps {
                git url: 'https://github.com/MawuliB/docker-app.git', branch: 'main'
                sh 'ls -l'
            }
        }

        stage('Test') {
            steps {
                createEnv()
                sh 'flake8 app.py'
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
                    sh 'ssh -o StrictHostKeyChecking=no ubuntu@44.204.192.188 "docker pull ${imageName}:latest && docker run -d -p 5000:5000 ${imageName}:latest"'
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