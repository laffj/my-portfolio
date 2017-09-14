#using boto3 for AWS CLI, StringIO, zipfile  module
# using mimetypes to correct file association on upload
import boto3
import StringIO
import zipfile
import mimetypes

# assign variable portfolio_bucket to appropriate buckets
s3 = boto3.resource('s3')
portfolio_bucket = s3.Bucket('portfolio.johnlaffey.net')

build_bucket = s3.Bucket('portfoliocode.johnlaffey.net')

# d/l into memory
portfolio_zip = StringIO.StringIO()
build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

# upload extracted files to public bucket with permissions
with zipfile.ZipFile(portfolio_zip) as myzip:
    for nm in myzip.namelist():
        obj = myzip.open(nm)
        portfolio_bucket.upload_fileobj(obj, nm,
        ExtraArgs={'ContentType': mimetypes.guess_type(nm) [0]})
        portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
