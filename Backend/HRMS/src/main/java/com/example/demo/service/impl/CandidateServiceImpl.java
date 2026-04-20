package com.example.demo.service.impl;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.example.demo.dto.CandidateRequestDto;
import com.example.demo.dto.CandidateResponseDto;
import com.example.demo.entity.Candidate;
import com.example.demo.enums.PipelineStage;
import com.example.demo.repository.CandidateRepository;
import com.example.demo.service.CandidateService;

import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
@Transactional
public class CandidateServiceImpl implements CandidateService {

	private final CandidateRepository candidateRepository;

	@Override
	public CandidateResponseDto createCandidate(CandidateRequestDto dto) {
		Candidate candidate = new Candidate();
		candidate.setFirstName(dto.getFirstName());
		candidate.setLastName(dto.getLastName());
		candidate.setEmail(dto.getEmail());
		candidate.setPhone(dto.getPhone());
		candidate.setLocation(dto.getLocation());
		candidate.setYearsOfExperience(dto.getYearsOfExperience());
		candidate.setDepartment(dto.getDepartment());
		candidate.setSkills(dto.getSkills());
		candidate.setCurrentCompany(dto.getCurrentCompany());
		candidate.setCurrentCtc(dto.getCurrentCtc());
		candidate.setEducation(dto.getEducation());
		candidate.setCurrentStage(dto.getCurrentStage() != null ? dto.getCurrentStage() : PipelineStage.APPLIED);

		Candidate savedCandidate = candidateRepository.save(candidate);
		return convertToResponseDto(savedCandidate);
	}

	@Override
	public CandidateResponseDto updateCandidate(Long id, CandidateRequestDto dto) {
		Candidate candidate = candidateRepository.findById(id)
				.orElseThrow(() -> new EntityNotFoundException("Candidate not found with id: " + id));

		candidate.setFirstName(dto.getFirstName());
		candidate.setLastName(dto.getLastName());
		candidate.setEmail(dto.getEmail());
		candidate.setPhone(dto.getPhone());
		candidate.setLocation(dto.getLocation());
		candidate.setYearsOfExperience(dto.getYearsOfExperience());
		candidate.setDepartment(dto.getDepartment());
		candidate.setSkills(dto.getSkills());
		candidate.setCurrentCompany(dto.getCurrentCompany());
		candidate.setCurrentCtc(dto.getCurrentCtc());
		candidate.setEducation(dto.getEducation());

		Candidate updatedCandidate = candidateRepository.save(candidate);
		return convertToResponseDto(updatedCandidate);
	}

	@Override
	public CandidateResponseDto getCandidateById(Long id) {
		Candidate candidate = candidateRepository.findById(id)
				.orElseThrow(() -> new EntityNotFoundException("Candidate not found with id: " + id));
		return convertToResponseDto(candidate);
	}

	@Override
	public Page<CandidateResponseDto> getAllCandidates(Pageable pageable) {
		return candidateRepository.findAll(pageable).map(this::convertToResponseDto);
	}

	@Override
	public void deleteCandidate(Long id) {
		if (!candidateRepository.existsById(id)) {
			throw new EntityNotFoundException("Candidate not found with id: " + id);
		}
		candidateRepository.deleteById(id);
	}

	@Override
	public CandidateResponseDto updatePipelineStage(Long id, String stage) {
		Candidate candidate = candidateRepository.findById(id)
				.orElseThrow(() -> new EntityNotFoundException("Candidate not found with id: " + id));

		PipelineStage newStage = PipelineStage.valueOf(stage.toUpperCase());
		candidate.updateStage(newStage);

		Candidate updatedCandidate = candidateRepository.save(candidate);
		return convertToResponseDto(updatedCandidate);
	}

	@Override
	public List<CandidateResponseDto> searchCandidatesByName(String name) {
		return candidateRepository.searchByName(name).stream().map(this::convertToResponseDto)
				.collect(Collectors.toList());
	}

	@Override
	public Page<CandidateResponseDto> searchCandidatesBySkill(String skill, Pageable pageable) {
		return candidateRepository.findBySkillsContainingIgnoreCase(skill, pageable).map(this::convertToResponseDto);
	}

	private CandidateResponseDto convertToResponseDto(Candidate candidate) {
		CandidateResponseDto dto = new CandidateResponseDto();
		dto.setId(candidate.getId());
		dto.setFirstName(candidate.getFirstName());
		dto.setLastName(candidate.getLastName());
		dto.setEmail(candidate.getEmail());
		dto.setPhone(candidate.getPhone());
		dto.setLocation(candidate.getLocation());
		dto.setYearsOfExperience(candidate.getYearsOfExperience());
		dto.setDepartment(candidate.getDepartment());
		dto.setSkills(candidate.getSkills());
		dto.setCurrentCompany(candidate.getCurrentCompany());
		dto.setCurrentCtc(candidate.getCurrentCtc());
		dto.setEducation(candidate.getEducation());
		dto.setCurrentStage(candidate.getCurrentStage());
		dto.setFullName(candidate.getFullName());
		dto.setCreatedAt(candidate.getCreatedAt());
		dto.setUpdatedAt(candidate.getUpdatedAt());
		return dto;
	}
}