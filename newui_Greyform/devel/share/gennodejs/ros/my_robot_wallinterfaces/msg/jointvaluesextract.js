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

class jointvaluesextract {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.joint_values = null;
      this.placementcoord = null;
    }
    else {
      if (initObj.hasOwnProperty('joint_values')) {
        this.joint_values = initObj.joint_values
      }
      else {
        this.joint_values = [];
      }
      if (initObj.hasOwnProperty('placementcoord')) {
        this.placementcoord = initObj.placementcoord
      }
      else {
        this.placementcoord = [];
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type jointvaluesextract
    // Serialize message field [joint_values]
    bufferOffset = _arraySerializer.float64(obj.joint_values, buffer, bufferOffset, null);
    // Serialize message field [placementcoord]
    bufferOffset = _arraySerializer.int32(obj.placementcoord, buffer, bufferOffset, null);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type jointvaluesextract
    let len;
    let data = new jointvaluesextract(null);
    // Deserialize message field [joint_values]
    data.joint_values = _arrayDeserializer.float64(buffer, bufferOffset, null)
    // Deserialize message field [placementcoord]
    data.placementcoord = _arrayDeserializer.int32(buffer, bufferOffset, null)
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += 8 * object.joint_values.length;
    length += 4 * object.placementcoord.length;
    return length + 8;
  }

  static datatype() {
    // Returns string type for a message object
    return 'my_robot_wallinterfaces/jointvaluesextract';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return 'bde6b642b6d906e5d1da1cf7db201cda';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    float64[] joint_values
    int32[] placementcoord
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new jointvaluesextract(null);
    if (msg.joint_values !== undefined) {
      resolved.joint_values = msg.joint_values;
    }
    else {
      resolved.joint_values = []
    }

    if (msg.placementcoord !== undefined) {
      resolved.placementcoord = msg.placementcoord;
    }
    else {
      resolved.placementcoord = []
    }

    return resolved;
    }
};

module.exports = jointvaluesextract;
