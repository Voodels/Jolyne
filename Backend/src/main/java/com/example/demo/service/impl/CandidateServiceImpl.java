package com.example.demo.service.impl;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import com.cloudinary.Cloudinary;
import com.cloudinary.utils.ObjectUtils;
import com.example.demo.dto.CandidateRequestDto;
import com.example.demo.dto.CandidateResponseDto;
import com.example.demo.entity.Candidate;
import com.example.demo.enums.PipelineStage;
import com.example.demo.repository.CandidateRepository;
import com.example.demo.service.CandidateService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
@Transactional
public class CandidateServiceImpl implements CandidateService {

    private final CandidateRepository candidateRepository;
    private final Cloudinary cloudinary;
    private final ObjectMapper objectMapper;

    // =========================
    // FILE UPLOAD
    // =========================
    @Override
    public String uploadResume(MultipartFile file) {
        try {
            Map uploadResult = cloudinary.uploader().upload(
                    file.getBytes(),
                    ObjectUtils.asMap("resource_type", "raw")
            );
            return uploadResult.get("secure_url").toString();
        } catch (IOException e) {
            throw new RuntimeException("Failed to upload file");
        }
    }

    // =========================
    // CREATE (NORMAL)
    // =========================
    @Override
    public CandidateResponseDto createCandidate(CandidateRequestDto dto) {
        Candidate candidate = mapToEntity(dto);
        return convertToResponseDto(candidateRepository.save(candidate));
    }

    // =========================
    // CREATE FROM FULL JSON 🔥
    // =========================
    @Override
    public CandidateResponseDto createFromResumeJson(String json) {
        try {
            JsonNode node = objectMapper.readTree(json);

            Candidate candidate = new Candidate();

            candidate.setFullName(getText(node, "fullName"));
            candidate.setFirstName(getText(node, "firstName"));
            candidate.setLastName(getText(node, "lastName"));
            candidate.setEmail(getText(node, "email"));
            candidate.setPhone(getText(node, "phone"));

            candidate.setSkills(node.get("skills") != null ? node.get("skills").toString() : null);
            candidate.setExperienceDetails(node.get("experience") != null ? node.get("experience").toString() : null);
            candidate.setEducationDetails(node.get("education") != null ? node.get("education").toString() : null);
            candidate.setProjects(node.get("projects") != null ? node.get("projects").toString() : null);

            candidate.setCurrentStage(PipelineStage.APPLIED);

            return convertToResponseDto(candidateRepository.save(candidate));

        } catch (Exception e) {
            throw new RuntimeException("Failed to parse resume JSON");
        }
    }

    // =========================
    // UPDATE (NORMAL)
    // =========================
    @Override
    public CandidateResponseDto updateCandidate(Long id, CandidateRequestDto dto) {
        Candidate candidate = getCandidate(id);
        mapToExistingEntity(dto, candidate);
        return convertToResponseDto(candidateRepository.save(candidate));
    }

    // =========================
    // UPDATE FULL JSON
    // =========================
    @Override
    public CandidateResponseDto updateFromResumeJson(Long id, String json) {
        Candidate candidate = getCandidate(id);

        try {
            JsonNode node = objectMapper.readTree(json);

            candidate.setFullName(getText(node, "fullName"));
            candidate.setSkills(node.get("skills") != null ? node.get("skills").toString() : null);
            candidate.setExperienceDetails(node.get("experience") != null ? node.get("experience").toString() : null);

            return convertToResponseDto(candidateRepository.save(candidate));

        } catch (Exception e) {
            throw new RuntimeException("Failed to update resume JSON");
        }
    }

    // =========================
    // GET
    // =========================
    @Override
    public CandidateResponseDto getCandidateById(Long id) {
        return convertToResponseDto(getCandidate(id));
    }

    @Override
    public Page<CandidateResponseDto> getAllCandidates(Pageable pageable) {
        return candidateRepository.findAll(pageable).map(this::convertToResponseDto);
    }

    // =========================
    // DELETE
    // =========================
    @Override
    public void deleteCandidate(Long id) {
        if (!candidateRepository.existsById(id)) {
            throw new EntityNotFoundException("Candidate not found");
        }
        candidateRepository.deleteById(id);
    }

    // =========================
    // PIPELINE
    // =========================
    @Override
    public CandidateResponseDto updatePipelineStage(Long id, String stage) {
        Candidate candidate = getCandidate(id);
        candidate.updateStage(PipelineStage.valueOf(stage.toUpperCase()));
        return convertToResponseDto(candidateRepository.save(candidate));
    }

    // =========================
    // SEARCH
    // =========================
    @Override
    public List<CandidateResponseDto> searchCandidatesByName(String name) {
        return candidateRepository.searchByName(name)
                .stream()
                .map(this::convertToResponseDto)
                .collect(Collectors.toList());
    }

    @Override
    public Page<CandidateResponseDto> searchCandidatesBySkill(String skill, Pageable pageable) {
        return candidateRepository.findBySkillsContainingIgnoreCase(skill, pageable)
                .map(this::convertToResponseDto);
    }

    // =========================
    // FILTER 🔥
    // =========================
    @Override
    public Page<CandidateResponseDto> filterCandidates(
            String name,
            String skill,
            String company,
            String domain,
            Double minExp,
            Double maxExp,
            Pageable pageable) {

        return candidateRepository.findAll(pageable)
                .map(this::convertToResponseDto)
                .map(dto -> dto) // placeholder (replace with spec later)
                ;
    }

    // =========================
    // GET RAW JSON
    // =========================
    @Override
    public String getResumeJson(Long id) {
        Candidate c = getCandidate(id);
        return c.getExperienceDetails(); // or combine multiple fields
    }

    // =========================
    // HELPER METHODS
    // =========================

    private Candidate getCandidate(Long id) {
        return candidateRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Candidate not found with id: " + id));
    }

    private Candidate mapToEntity(CandidateRequestDto dto) {
        Candidate c = new Candidate();

        mapToExistingEntity(dto, c);
        c.setCurrentStage(dto.getCurrentStage() != null ? dto.getCurrentStage() : PipelineStage.APPLIED);

        return c;
    }

    private void mapToExistingEntity(CandidateRequestDto dto, Candidate c) {

        c.setFullName(dto.getFullName());
        c.setFirstName(dto.getFirstName());
        c.setMiddleName(dto.getMiddleName());
        c.setLastName(dto.getLastName());

        c.setEmail(dto.getEmail());
        c.setPhone(dto.getPhone());
        c.setAlternatePhone(dto.getAlternatePhone());

        c.setLocation(dto.getLocation());
        c.setCity(dto.getCity());
        c.setState(dto.getState());
        c.setCountry(dto.getCountry());

        c.setYearsOfExperience(dto.getYearsOfExperience());
        c.setTotalExperienceYears(dto.getTotalExperienceYears());

        c.setDepartment(dto.getDepartment());

        c.setSkills(dto.getSkills());
        c.setSkillsDetailed(dto.getSkillsDetailed());

        c.setCurrentCompany(dto.getCurrentCompany());
        c.setCurrentCtc(dto.getCurrentCtc());

        c.setEducation(dto.getEducation());
        c.setEducationDetails(dto.getEducationDetails());

        c.setExperienceDetails(dto.getExperienceDetails());
        c.setProjects(dto.getProjects());

        c.setResumeUrl(dto.getResumeUrl());
        c.setResumeText(dto.getResumeText());
    }

    private CandidateResponseDto convertToResponseDto(Candidate c) {

        CandidateResponseDto dto = new CandidateResponseDto();

        dto.setId(c.getId());
        dto.setFullName(c.getFullName());
        dto.setFirstName(c.getFirstName());
        dto.setMiddleName(c.getMiddleName());
        dto.setLastName(c.getLastName());

        dto.setEmail(c.getEmail());
        dto.setPhone(c.getPhone());

        dto.setLocation(c.getLocation());
        dto.setCity(c.getCity());
        dto.setState(c.getState());
        dto.setCountry(c.getCountry());

        dto.setYearsOfExperience(c.getYearsOfExperience());
        dto.setTotalExperienceYears(c.getTotalExperienceYears());

        dto.setDepartment(c.getDepartment());

        dto.setSkills(c.getSkills());
        dto.setSkillsDetailed(c.getSkillsDetailed());

        dto.setCurrentCompany(c.getCurrentCompany());
        dto.setCurrentCtc(c.getCurrentCtc());

        dto.setEducation(c.getEducation());
        dto.setEducationDetails(c.getEducationDetails());

        dto.setExperienceDetails(c.getExperienceDetails());
        dto.setProjects(c.getProjects());

        dto.setCurrentStage(c.getCurrentStage());

        dto.setCreatedAt(c.getCreatedAt());
        dto.setUpdatedAt(c.getUpdatedAt());

        dto.setResumeUrl(c.getResumeUrl());

        return dto;
    }

    private String getText(JsonNode node, String field) {
        return node.has(field) && !node.get(field).isNull()
                ? node.get(field).asText()
                : null;
    }
}