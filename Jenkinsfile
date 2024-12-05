def appName = 'github-project'

pipeline {
    agent any
    stages {
        stage('VCSCheckout') {
            steps {
                git url: 'https://github.com/karthik-s-2024/github-project.git', branch: 'main'
                sh 'ls -l'
            }
        }
    }
}