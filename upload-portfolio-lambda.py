#using boto3 for AWS CLI, StringIO, zipfile  module
# using mimetypes to correct file association on upload
import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    # Identify the topic for confirmation email
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:275024349352:DeployPortfolioTopic')

    location = {
        "bucketName": 'portfoliocode.johnlaffey.net',
        "objectKey": 'portfoliobuild.zip'
    }

    # assign variable portfolio_bucket to appropriate buckets
    try:
        job = event.get("CodePipeline.job")

        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]

        print "Building from " + str(location)
        s3 = boto3.resource('s3')
        portfolio_bucket = s3.Bucket('portfolio.johnlaffey.net')

        build_bucket = s3.Bucket(location["bucketName"])

        # d/l into memory
        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)

        # upload extracted files to public bucket with permissions
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs={'Content-Type': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl.put(ACL='public-read')

            
        print "Deployment Complete!"
        # push the confirmation email
        topic.publish(Subject="New Portfolio Deployment", Message="Portfolio deployed successfully")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])

    except:
        topic.publish(Subject="Portfolio Deployment Failure", Message="Portfolio deployment failed, check logs")
        raise

    return 'Hello from Lambda'
