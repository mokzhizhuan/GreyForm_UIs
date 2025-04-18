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

class SelectionWall {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.wallselection = null;
      this.typeselection = null;
      this.picked_position = null;
    }
    else {
      if (initObj.hasOwnProperty('wallselection')) {
        this.wallselection = initObj.wallselection
      }
      else {
        this.wallselection = '';
      }
      if (initObj.hasOwnProperty('typeselection')) {
        this.typeselection = initObj.typeselection
      }
      else {
        this.typeselection = '';
      }
      if (initObj.hasOwnProperty('picked_position')) {
        this.picked_position = initObj.picked_position
      }
      else {
        this.picked_position = [];
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type SelectionWall
    // Serialize message field [wallselection]
    bufferOffset = _serializer.string(obj.wallselection, buffer, bufferOffset);
    // Serialize message field [typeselection]
    bufferOffset = _serializer.string(obj.typeselection, buffer, bufferOffset);
    // Serialize message field [picked_position]
    bufferOffset = _arraySerializer.int32(obj.picked_position, buffer, bufferOffset, null);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type SelectionWall
    let len;
    let data = new SelectionWall(null);
    // Deserialize message field [wallselection]
    data.wallselection = _deserializer.string(buffer, bufferOffset);
    // Deserialize message field [typeselection]
    data.typeselection = _deserializer.string(buffer, bufferOffset);
    // Deserialize message field [picked_position]
    data.picked_position = _arrayDeserializer.int32(buffer, bufferOffset, null)
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += _getByteLength(object.wallselection);
    length += _getByteLength(object.typeselection);
    length += 4 * object.picked_position.length;
    return length + 12;
  }

  static datatype() {
    // Returns string type for a message object
    return 'my_robot_wallinterfaces/SelectionWall';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return 'cec1748b8474fc5db64b113998095031';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    string wallselection
    string typeselection
    int32[] picked_position
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new SelectionWall(null);
    if (msg.wallselection !== undefined) {
      resolved.wallselection = msg.wallselection;
    }
    else {
      resolved.wallselection = ''
    }

    if (msg.typeselection !== undefined) {
      resolved.typeselection = msg.typeselection;
    }
    else {
      resolved.typeselection = ''
    }

    if (msg.picked_position !== undefined) {
      resolved.picked_position = msg.picked_position;
    }
    else {
      resolved.picked_position = []
    }

    return resolved;
    }
};

module.exports = SelectionWall;
