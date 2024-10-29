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
      this.stl_data = null;
      this.excelfile = null;
    }
    else {
      if (initObj.hasOwnProperty('stl_data')) {
        this.stl_data = initObj.stl_data
      }
      else {
        this.stl_data = [];
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
    // Serialize message field [stl_data]
    bufferOffset = _arraySerializer.uint8(obj.stl_data, buffer, bufferOffset, null);
    // Serialize message field [excelfile]
    bufferOffset = _serializer.string(obj.excelfile, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type FileExtractionMessage
    let len;
    let data = new FileExtractionMessage(null);
    // Deserialize message field [stl_data]
    data.stl_data = _arrayDeserializer.uint8(buffer, bufferOffset, null)
    // Deserialize message field [excelfile]
    data.excelfile = _deserializer.string(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += object.stl_data.length;
    length += _getByteLength(object.excelfile);
    return length + 8;
  }

  static datatype() {
    // Returns string type for a message object
    return 'my_robot_wallinterfaces/FileExtractionMessage';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return '81c918b74dbfb64e2d1abc77031a354e';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    uint8[] stl_data
    string excelfile
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new FileExtractionMessage(null);
    if (msg.stl_data !== undefined) {
      resolved.stl_data = msg.stl_data;
    }
    else {
      resolved.stl_data = []
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
