var QUEUE_URL = 'Link-to-your queue/RPi3-FIFO.fifo';
var AWS = require('aws-sdk');
var sqs = new AWS.SQS({region : 'us-west-2'});

exports.handler = function(event, context) {
  var params = {
    MessageBody: JSON.stringify(event),
    QueueUrl: QUEUE_URL,
    MessageGroupId: 'STRING_VALUE'
  };
  sqs.sendMessage(params, function(err,data){
    if(err) {
      console.log('error:',"Fail Send Message" + err);
      context.done('error', "ERROR Put SQS");  // ERROR with message
    }else{
      console.log('data:',data.MessageId);
      context.done(null,'');  // SUCCESS 
    }
  });
}