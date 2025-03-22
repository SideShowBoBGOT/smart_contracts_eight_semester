// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Library named after the full name (PIP)
library PanchenkoSerhiiVitaliyovich {
    // Function to parse ETH price from a string
    function PanchenkoSerhiiVitaliyovichParsePrice(string memory priceString) internal pure returns (uint256) {
        bytes memory priceBytes = bytes(priceString);
        
        // Find the position of '='
        uint256 equalPosition = 0;
        for (uint256 i = 0; i < priceBytes.length; i++) {
            if (priceBytes[i] == '=') {
                equalPosition = i + 1;
                break;
            }
        }
        
        // Parse the number
        uint256 price = 0;
        for (uint256 i = equalPosition; i < priceBytes.length; i++) {
            if (priceBytes[i] >= '0' && priceBytes[i] <= '9') {
                price = price * 10 + uint256(uint8(priceBytes[i]) - 48);
            }
            if (priceBytes[i] == '$') {
                break;
            }
        }
        
        return price;
    }
    
    // Function to generate weather comment
    function PanchenkoSerhiiVitaliyovichWeatherComment(int8 temperature) internal pure returns (string memory) {
        string memory comment;
        
        if (temperature < 0) {
            comment = "cold: ";
        } else if (temperature < 15) {
            comment = "cool: ";
        } else if (temperature < 25) {
            comment = "warm: ";
        } else {
            comment = "hot: ";
        }
        
        // Convert temperature to string
        string memory tempStr = PanchenkoSerhiiVitaliyovichIntToString(temperature);
        
        return string(abi.encodePacked(comment, tempStr, " C"));
    }
    
    // Helper function to convert int to string
    function PanchenkoSerhiiVitaliyovichIntToString(int8 value) internal pure returns (string memory) {
        if (value == 0) {
            return "0";
        }
        
        bool isNegative = value < 0;
        uint8 absValue = isNegative ? uint8(-value) : uint8(value);
        
        uint8 digits = 0;
        uint8 temp = absValue;
        
        while (temp > 0) {
            digits++;
            temp /= 10;
        }
        
        bytes memory buffer = new bytes(isNegative ? digits + 1 : digits);
        
        if (isNegative) {
            buffer[0] = '-';
        }
        
        uint8 index = uint8(buffer.length) - 1;
        temp = absValue;
        
        while (temp > 0) {
            buffer[index--] = bytes1(uint8(48 + (temp % 10)));
            temp /= 10;
        }
        
        return string(buffer);
    }
}

contract Panchenko {
    using PanchenkoSerhiiVitaliyovich for *;
    
    address public owner;
    uint256 public constant REQUIRED_ETH = 6; // [DD] = 06
    uint256 public constant REQUIRED_ADDRESSES = 3; // [MM]/2 = 03/2 rounded up to 3
    uint256 public constant MARKET_RATE = 2004; // [YYYY] = 2004
    
    mapping(address => bool) public contributors;
    uint256 public contributorsCount;
    
    event ContributionReceived(address indexed contributor, uint256 amount);
    event PriceConverted(string priceString, uint256 price);
    event WeatherCommented(int8 temperature, string comment);
    
    constructor() {
        owner = msg.sender;
    }
    
    function PanchenkoSerhiiVitaliyovichContribute() public payable {
        require(msg.value == REQUIRED_ETH * 1 ether, "Must send exactly 6 ETH");
        require(!contributors[msg.sender], "Already contributed");
        require(contributorsCount < REQUIRED_ADDRESSES, "Maximum contributors reached");
        
        contributors[msg.sender] = true;
        contributorsCount++;
        
        emit ContributionReceived(msg.sender, msg.value);
    }
    
    function PanchenkoSerhiiVitaliyovichGetPrice(string memory priceString) public returns (uint256) {
        uint256 price = PanchenkoSerhiiVitaliyovich.PanchenkoSerhiiVitaliyovichParsePrice(priceString);
        emit PriceConverted(priceString, price);
        return price;
    }
    
    function PanchenkoSerhiiVitaliyovichGetWeather(int8 temperature) public returns (string memory) {
        string memory comment = PanchenkoSerhiiVitaliyovich.PanchenkoSerhiiVitaliyovichWeatherComment(temperature);
        emit WeatherCommented(temperature, comment);
        return comment;
    }
    
    function PanchenkoSerhiiVitaliyovichWithdraw() public {
        require(msg.sender == owner, "Only owner can withdraw");
        require(contributorsCount == REQUIRED_ADDRESSES, "Need all contributions first");
        
        payable(owner).transfer(address(this).balance);
    }
    
    function PanchenkoSerhiiVitaliyovichGetBalance() public view returns (uint256) {
        return address(this).balance;
    }
}