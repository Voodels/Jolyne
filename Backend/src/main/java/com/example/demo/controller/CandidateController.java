package com.example.demo.controller;

import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import org.springframework.web.multipart.MultipartFile;

import com.example.demo.dto.CandidateRequestDto;
import com.example.demo.dto.CandidateResponseDto;
import com.example.demo.service.CandidateService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/v1/candidates")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class CandidateController {

    private final CandidateService candidateService;

    // =========================
    // CREATE CANDIDATE
    // =========================
    @PostMapping
    public ResponseEntity<CandidateResponseDto> createCandidate(
            @Valid @RequestBody CandidateRequestDto candidateDto) {

        return ResponseEntity.status(HttpStatus.CREATED)
                .body(candidateService.createCandidate(candidateDto));
    }

    // =========================
    // CREATE FROM FULL RESUME JSON
    // =========================
    @PostMapping("/full")
    public ResponseEntity<CandidateResponseDto> createFromFullResume(
            @RequestBody String resumeJson) {

        CandidateResponseDto response = candidateService.createFromResumeJson(resumeJson);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    // =========================
    // GET BY ID
    // =========================
    @GetMapping("/{id}")
    public ResponseEntity<CandidateResponseDto> getCandidateById(@PathVariable Long id) {
        return ResponseEntity.ok(candidateService.getCandidateById(id));
    }

    // =========================
    // GET ALL (PAGINATED)
    // =========================
    @GetMapping
    public ResponseEntity<Page<CandidateResponseDto>> getAllCandidates(
            @PageableDefault(size = 20, sort = "createdAt", direction = Sort.Direction.DESC)
            Pageable pageable) {

        return ResponseEntity.ok(candidateService.getAllCandidates(pageable));
    }

    // =========================
    // UPDATE FULL
    // =========================
    @PutMapping("/{id}")
    public ResponseEntity<CandidateResponseDto> updateCandidate(
            @PathVariable Long id,
            @Valid @RequestBody CandidateRequestDto candidateDto) {

        return ResponseEntity.ok(candidateService.updateCandidate(id, candidateDto));
    }

    // =========================
    // UPDATE USING FULL JSON
    // =========================
    @PutMapping("/{id}/full")
    public ResponseEntity<CandidateResponseDto> updateFromResumeJson(
            @PathVariable Long id,
            @RequestBody String resumeJson) {

        return ResponseEntity.ok(candidateService.updateFromResumeJson(id, resumeJson));
    }

    // =========================
    // DELETE
    // =========================
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteCandidate(@PathVariable Long id) {
        candidateService.deleteCandidate(id);
        return ResponseEntity.noContent().build();
    }

    // =========================
    // UPDATE PIPELINE STAGE
    // =========================
    @PatchMapping("/{id}/stage")
    public ResponseEntity<CandidateResponseDto> updatePipelineStage(
            @PathVariable Long id,
            @RequestParam String stage) {

        return ResponseEntity.ok(candidateService.updatePipelineStage(id, stage));
    }

    // =========================
    // RESUME UPLOAD (Cloudinary)
    // =========================
    @PostMapping("/upload-resume")
    public ResponseEntity<String> uploadResume(
            @RequestParam("file") MultipartFile file) {

        return ResponseEntity.ok(candidateService.uploadResume(file));
    }

    // =========================
    // SEARCH BY NAME
    // =========================
    @GetMapping("/search")
    public ResponseEntity<List<CandidateResponseDto>> searchByName(
            @RequestParam String name) {

        return ResponseEntity.ok(candidateService.searchCandidatesByName(name));
    }

    // =========================
    // SEARCH BY SKILL (BASIC)
    // =========================
    @GetMapping("/skill")
    public ResponseEntity<Page<CandidateResponseDto>> searchBySkill(
            @RequestParam String skill,
            @PageableDefault(size = 20) Pageable pageable) {

        return ResponseEntity.ok(candidateService.searchCandidatesBySkill(skill, pageable));
    }

    // =========================
    // ADVANCED FILTER (NEW 🔥)
    // =========================
    @GetMapping("/filter")
    public ResponseEntity<Page<CandidateResponseDto>> filterCandidates(
            @RequestParam(required = false) String name,
            @RequestParam(required = false) String skill,
            @RequestParam(required = false) String company,
            @RequestParam(required = false) String domain,
            @RequestParam(required = false) Double minExperience,
            @RequestParam(required = false) Double maxExperience,
            @PageableDefault(size = 20) Pageable pageable) {

        return ResponseEntity.ok(
                candidateService.filterCandidates(
                        name, skill, company, domain, minExperience, maxExperience, pageable
                )
        );
    }

    // =========================
    // GET RAW RESUME JSON
    // =========================
    @GetMapping("/{id}/resume-json")
    public ResponseEntity<String> getResumeJson(@PathVariable Long id) {
        return ResponseEntity.ok(candidateService.getResumeJson(id));
    }

    // =========================
    // PARSE RESUME VIA AFFINDA (PROXY)
    // =========================
    @PostMapping("/parse-resume")
    public ResponseEntity<String> parseResumeViaAffinda(
            @RequestParam("file") MultipartFile file) {
        return ResponseEntity.ok(candidateService.parseResumeWithAffinda(file));
    }
} 