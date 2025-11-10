// Auto-generated. Do not edit!

// (in-package my_robot_wallinterfaces.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;

//-----------------------------------------------------------

class FileExtractionMessage {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.directory = null;
      this.excelfile = null;
    }
    else {
      if (initObj.hasOwnProperty('directory')) {
        this.directory = initObj.directory
      }
      else {
        this.directory = '';
      }
      if (initObj.hasOwnProperty('excelfile')) {
        this.excelfile = initObj.excelfile
      }
      else {
        this.excelfile = '';
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type FileExtractionMessage
    // Serialize message field [directory]
    bufferOffset = _serializer.string(obj.directory, buffer, bufferOffset);
    // Serialize message field [excelfile]
    bufferOffset = _serializer.string(obj.excelfile, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type FileExtractionMessage
    let len;
    let data = new FileExtractionMessage(null);
    // Deserialize message field [directory]
    data.directory = _deserializer.string(buffer, bufferOffset);
    // Deserialize message field [excelfile]
    data.excelfile = _deserializer.string(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += _getByteLength(object.directory);
    length += _getByteLength(object.excelfile);
    return length + 8;
  }

  static datatype() {
    // Returns string type for a message object
    return 'my_robot_wallinterfaces/FileExtractionMessage';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return 'd217064ce75170f28ac78f629dbe4223';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    string directory
    string excelfile
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new FileExtractionMessage(null);
    if (msg.directory !== undefined) {
      resolved.directory = msg.directory;
    }
    else {
      resolved.directory = ''
    }

    if (msg.excelfile !== undefined) {
      resolved.excelfile = msg.excelfile;
    }
    else {
      resolved.excelfile = ''
    }

    return resolved;
    }
};

module.exports = FileExtractionMessage;
