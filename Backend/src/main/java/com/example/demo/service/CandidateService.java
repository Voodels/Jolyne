package com.example.demo.service;

import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.web.multipart.MultipartFile;

import com.example.demo.dto.CandidateRequestDto;
import com.example.demo.dto.CandidateResponseDto;

public interface CandidateService {
	CandidateResponseDto createCandidate(CandidateRequestDto candidateDto);

	CandidateResponseDto updateCandidate(Long id, CandidateRequestDto candidateDto);

	CandidateResponseDto getCandidateById(Long id);

	Page<CandidateResponseDto> getAllCandidates(Pageable pageable);

	void deleteCandidate(Long id);

	String uploadResume(MultipartFile file);

	CandidateResponseDto createFromResumeJson(String json);

CandidateResponseDto updateFromResumeJson(Long id, String json);

Page<CandidateResponseDto> filterCandidates(
    String name,
    String skill,
    String company,
    String domain,
    Double minExperience,
    Double maxExperience,
    Pageable pageable
);


String getResumeJson(Long id);
	
	CandidateResponseDto updatePipelineStage(Long id, String stage);

	List<CandidateResponseDto> searchCandidatesByName(String name);

	Page<CandidateResponseDto> searchCandidatesBySkill(String skill, Pageable pageable);
}