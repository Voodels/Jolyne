package com.example.demo.entity;

import java.time.LocalDateTime;

import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import com.example.demo.enums.Department;
import com.example.demo.enums.PipelineStage;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "candidates")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
public class Candidate {

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long id;

	// Personal Information
	@Column(nullable = false)
	private String firstName;

	@Column(nullable = false)
	private String lastName;

	@Column(unique = true, nullable = false)
	private String email;

	private String phone;
	private String location;

	// Professional Information
	private Integer yearsOfExperience;

	@Enumerated(EnumType.STRING)
	private Department department;

	@Column(columnDefinition = "TEXT")
	private String skills; // comma-separated, e.g., "Java,Spring,PostgreSQL"

	private String currentCompany;
	private String currentCtc; // Cost to Company (Salary)

	@Column(columnDefinition = "TEXT")
	private String resumeText; // Extracted text from uploaded resume

	private String education; // e.g., "B.Tech in Computer Science"

	// Recruitment Pipeline
	@Enumerated(EnumType.STRING)
	private PipelineStage currentStage;

	@Column(columnDefinition = "jsonb")
	private String stageHistory; // Stores JSON array of stage transitions

	// AI & Vector Data
//	@Column(columnDefinition = "vector(1536)")
//	private float[] embedding; // Stores the 1536-dimensional vector

	// Timestamps
	@CreationTimestamp
	@Column(updatable = false)
	private LocalDateTime createdAt;

	@UpdateTimestamp
	private LocalDateTime updatedAt;

	// Helper method to get full name
	public String getFullName() {
		return firstName + " " + lastName;
	}

	// Helper method to update stage with history
	public void updateStage(PipelineStage newStage) {
		// Logic to update stage and append to stageHistory
		this.currentStage = newStage;
	}

	public Long getId() {
		return id;
	}

	public void setId(Long id) {
		this.id = id;
	}

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

	public void setDepartment(Department department) {
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

	public String getResumeText() {
		return resumeText;
	}

	public void setResumeText(String resumeText) {
		this.resumeText = resumeText;
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

	public String getStageHistory() {
		return stageHistory;
	}

	public void setStageHistory(String stageHistory) {
		this.stageHistory = stageHistory;
	}

//	public float[] getEmbedding() {
//		return embedding;
//	}
//
//	public void setEmbedding(float[] embedding) {
//		this.embedding = embedding;
//	}

	public LocalDateTime getCreatedAt() {
		return createdAt;
	}

	public void setCreatedAt(LocalDateTime createdAt) {
		this.createdAt = createdAt;
	}

	public LocalDateTime getUpdatedAt() {
		return updatedAt;
	}

	public void setUpdatedAt(LocalDateTime updatedAt) {
		this.updatedAt = updatedAt;
	}

}