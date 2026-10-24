pipeline {
    agent any

    // No public URL for webhooks on a home laptop, so poll GitHub every 2 minutes
    triggers { pollSCM('H/2 * * * *') }

    environment {
        REGISTRY = 'ghcr.io'
        IMAGE    = 'ghcr.io/mohitbhardwaj0208/storeops-api'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                }
            }
        }

        stage('Test') {
            steps {
                sh '''
                  docker run --rm -v "$PWD":/src -w /src python:3.12-slim \
                    sh -c "pip install -q -r app/requirements.txt && pytest app/tests -q"
                '''
            }
        }

        stage('Build image') {
            steps {
                sh "docker build -t ${IMAGE}:${GIT_SHORT} -t ${IMAGE}:latest ."
            }
        }

        stage('Push image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'ghcr',
                                                  usernameVariable: 'REG_USER',
                                                  passwordVariable: 'REG_TOKEN')]) {
                    sh '''
                      echo "$REG_TOKEN" | docker login ${REGISTRY} -u "$REG_USER" --password-stdin
                      docker push ${IMAGE}:${GIT_SHORT}
                      docker push ${IMAGE}:latest
                      docker logout ${REGISTRY}
                    '''
                }
            }
        }
    }

    post {
        success { echo "Pushed ${IMAGE}:${GIT_SHORT}" }
        failure { echo "Pipeline failed - image NOT pushed" }
    }
}
