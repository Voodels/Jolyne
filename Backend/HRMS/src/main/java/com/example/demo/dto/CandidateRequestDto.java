package com.example.demo.dto;

import com.example.demo.enums.Department;
import com.example.demo.enums.PipelineStage;

import lombok.Data;

@Data
public class CandidateRequestDto {

	private String firstName;

	private String lastName;

	private String email;

	private String phone;
	private String location;
	private Integer yearsOfExperience;
	private Department department;
	private String skills;
	private String currentCompany;
	private String currentCtc;
	private String education;
	private PipelineStage currentStage;

	public String getFirstName() {
		return firstName;
	}

	public void setFirstName(String firstName) {
		this.firstName = firstName;
	}

	public String getLastName() {
		return lastName;
	}

	public void setLastName(String lastName) {
		this.lastName = lastName;
	}

	public String getEmail() {
		return email;
	}

	public void setEmail(String email) {
		this.email = email;
	}

	public String getPhone() {
		return phone;
	}

	public void setPhone(String phone) {
		this.phone = phone;
	}

	public String getLocation() {
		return location;
	}

	public void setLocation(String location) {
		this.location = location;
	}

	public Integer getYearsOfExperience() {
		return yearsOfExperience;
	}

	public void setYearsOfExperience(Integer yearsOfExperience) {
		this.yearsOfExperience = yearsOfExperience;
	}

	public Department getDepartment() {
		return department;
	}

	public void setDesignation(Department department) {
		this.department = department;
	}

	public String getSkills() {
		return skills;
	}

	public void setSkills(String skills) {
		this.skills = skills;
	}

	public String getCurrentCompany() {
		return currentCompany;
	}

	public void setCurrentCompany(String currentCompany) {
		this.currentCompany = currentCompany;
	}

	public String getCurrentCtc() {
		return currentCtc;
	}

	public void setCurrentCtc(String currentCtc) {
		this.currentCtc = currentCtc;
	}

	public String getEducation() {
		return education;
	}

	public void setEducation(String education) {
		this.education = education;
	}

	public PipelineStage getCurrentStage() {
		return currentStage;
	}

	public void setCurrentStage(PipelineStage currentStage) {
		this.currentStage = currentStage;
	}

}