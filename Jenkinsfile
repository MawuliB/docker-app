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

def gitSha() {
    return sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
}

def loginToDockerHub() {
    withCredentials([usernamePassword(credentialsId: 'docker-hub-cred', usernameVariable: 'DOCKER_HUB_USERNAME', passwordVariable: 'DOCKER_HUB_PASSWORD')]) {
        sh "echo ${DOCKER_HUB_PASSWORD} | docker login -u ${DOCKER_HUB_USERNAME} --password-stdin"
    }
}

def buildAndPushToDockerHub() {
    sh '''
        docker build -t ${IMAGE_NAME}:${GIT_SHA} .
        docker push ${IMAGE_NAME}:${GIT_SHA}
    '''
}

def cleanup() {
    sh 'docker volume prune -f && docker system prune -f'
}

pipeline {
    agent {
        label 'agent1'
    }
    
    tools {
        jdk 'jdk21'
    }

    environment {
        APP_NAME = 'docker-app'
        IMAGE_NAME = 'mawulib/docker-app'
        GIT_SHA = gitSha()
        JAVA_HOME = tool 'jdk21'
        PATH = "${env.JAVA_HOME}/bin:${env.PATH}"
    }

    stages {
        stage('VCSCheckout') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-cred', usernameVariable: 'GITHUB_USERNAME', passwordVariable: 'GITHUB_PASSWORD')]) {
                    git url: 'https://${GITHUB_USERNAME}:${GITHUB_PASSWORD}@github.com/MawuliB/docker-app.git', branch: 'main'
                }
                createEnv()
            }
        }

        stage('Testing') {
            steps {
                sh '. .venv/bin/activate && flake8 main.py'
            }
        }

        stage("SonarQube analysis") {
            steps {
                withSonarQubeEnv('sonarqube') {
                    withEnv(["JAVA_HOME=${tool 'jdk17'}", 
                            "PATH=${tool 'jdk17'}/bin:/opt/sonar-scanner/bin:${env.PATH}"]) {
                        sh '''
                            sonar-scanner \
                                -Dsonar.projectKey=docker-app \
                                -Dsonar.sources=. \
                                -Dsonar.python.version=3.x \
                                -Dsonar.qualitygate.wait=true \
                                -Dsonar.python.flake8.reportPaths=flake8-report.txt
                        '''
                    }
                }
            }
        }

        stage('Building') {
            steps {
                loginToDockerHub()
                buildAndPushToDockerHub()
            }
        }

        stage('Deployment') {
            steps {
                sshagent(['ec2-ssh-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ubuntu@3.91.239.93 "docker pull ${IMAGE_NAME}:${GIT_SHA} && docker stop ${APP_NAME} || true && docker rm ${APP_NAME} || true && docker run -d -p 5000:5000 --name ${APP_NAME} ${IMAGE_NAME}:${GIT_SHA}"
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
            cleanWs()
        }
        success {
            sh 'echo "Pipeline completed successfully for ${APP_NAME} :)"'
        }
        failure {
            sh 'echo "Pipeline completed with errors for ${APP_NAME} :("'
        }
    }
}