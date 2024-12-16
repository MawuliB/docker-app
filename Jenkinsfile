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
        BRANCH_NAME = "${env.BRANCH_NAME}"
    }

    stages {
        stage('Testing') {
            steps {
                createEnv()
                sh '. .venv/bin/activate && flake8 main.py'
            }
        }

        stage("SonarQube analysis") {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    withSonarQubeEnv('sonarqube') {
                        withEnv(["JAVA_HOME=${tool 'jdk17'}", 
                                "PATH=${tool 'jdk17'}/bin:/opt/sonar-scanner/bin:${env.PATH}"]) {
                            sh '''
                                . .venv/bin/activate

                                # Clean up any existing report files
                                rm -f report-task.txt
                                rm -rf .scannerwork
                                
                                # Create empty coverage and test reports if no tests exist
                                if [ -n "$(find . -name '*_test.py' -o -name '*_tests.py')" ]; then
                                    python -m pytest --cov=. --cov-report=xml:coverage.xml --junitxml=test-results.xml || true
                                else
                                    echo '' > coverage.xml
                                    echo '' > test-results.xml
                                fi
                                
                                # Run flake8 only on Python files
                                flake8 $(find . -name "*.py" ! -path "./.venv/*") --output-file=flake8-report.txt || true
                                
                                # Run sonar-scanner with additional parameters
                                sonar-scanner \
                                    -Dsonar.host.url=https://sonar-server.free-sns.live \
                                    -Dsonar.projectKey=docker-app \
                                    -Dsonar.projectBaseDir=${WORKSPACE} \
                                    -Dsonar.sources=. \
                                    -Dsonar.python.version=3.9 \
                                    -Dsonar.qualitygate.wait=true \
                                    -Dsonar.python.flake8.reportPaths=${WORKSPACE}/flake8-report.txt \
                                    -Dsonar.sourceEncoding=UTF-8 \
                                    -Dsonar.python.coverage.reportPaths=${WORKSPACE}/coverage.xml \
                                    -Dsonar.test.inclusions=**/*_test.py,**/*_tests.py \
                                    -Dsonar.python.xunit.reportPath=${WORKSPACE}/test-results.xml \
                                    -Dsonar.exclusions=.venv/**,**/*.pyc,**/__pycache__/** \
                                    -Dsonar.working.directory=${WORKSPACE}/.scannerwork
                            '''
                        }
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