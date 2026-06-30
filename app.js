// ==========================================================================
// CIT Coders Arena - Application Logic & Controllers
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Check if data script loaded successfully
    if (!window.knightsData) {
        console.error("Roster database data.js failed to load.");
        document.getElementById('knights-grid-container').innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-triangle-exclamation" style="color: #ef4444;"></i>
                <h3>Roster Database Offline</h3>
                <p>Could not locate the student profiles database (data.js). Please run the scraper script.</p>
            </div>
        `;
        return;
    }

    // Clean data and parse numeric stats for sorting/filtering
    const rawData = window.knightsData;
    const roster = rawData.map(c => {
        const leetcodeRating = parseInt(c.leetcode_rating) || 1400;
        const codeforcesRating = parseInt(c.codeforces_rating) || 1200;
        const githubRepos = parseInt(c.github_repos) || 0;
        
        let solvedCount = 0;
        if (c.solved_count) {
            solvedCount = parseInt(c.solved_count.replace('+', '').trim()) || 0;
        }

        // Clean name
        const cleanName = c.name.trim ? c.name.trim() : c.name;

        return {
            ...c,
            name: cleanName,
            leetcodeRating,
            codeforcesRating,
            githubRepos,
            solvedCount
        };
    });

    // Roster UI Elements
    const gridContainer = document.getElementById('knights-grid-container');
    const searchInput = document.getElementById('search-input');
    const clearSearchBtn = document.getElementById('clear-search');
    const sortSelect = document.getElementById('sort-select');
    const filterChips = document.querySelectorAll('.filter-chip');
    
    // Stats Elements
    const statTotalCoders = document.getElementById('stat-total-coders');
    const statPeakRating = document.getElementById('stat-peak-rating');
    const statTotalRepos = document.getElementById('stat-total-repos');
    const statActiveDuelists = document.getElementById('stat-active-duelists');
    const deptMetricsContainer = document.getElementById('dept-metrics-container');

    // Code Duel Arena Elements
    const fighterASelect = document.getElementById('fighter-a-select');
    const fighterBSelect = document.getElementById('fighter-b-select');
    const initiateDuelBtn = document.getElementById('initiate-duel-btn');
    const duelBoard = document.getElementById('duel-board');
    
    const duelNameA = document.getElementById('duel-name-a');
    const duelDeptA = document.getElementById('duel-dept-a');
    const duelAvatarA = document.getElementById('duel-avatar-a');
    const healthBarA = document.getElementById('health-bar-a');
    
    const duelNameB = document.getElementById('duel-name-b');
    const duelDeptB = document.getElementById('duel-dept-b');
    const duelAvatarB = document.getElementById('duel-avatar-b');
    const healthBarB = document.getElementById('health-bar-b');

    const duelValLcA = document.getElementById('duel-val-lc-a');
    const duelValLcB = document.getElementById('duel-val-lc-b');
    const duelValSolvedA = document.getElementById('duel-val-solved-a');
    const duelValSolvedB = document.getElementById('duel-val-solved-b');
    const duelValCfA = document.getElementById('duel-val-cf-a');
    const duelValCfB = document.getElementById('duel-val-cf-b');
    const duelValGhA = document.getElementById('duel-val-gh-a');
    const duelValGhB = document.getElementById('duel-val-gh-b');

    // Terminal Modal Scanner Elements
    const scanModal = document.getElementById('scan-modal');
    const terminalConsole = document.getElementById('terminal-console');
    const terminalScanResult = document.getElementById('terminal-scan-result');
    const closeScanBtn = document.getElementById('close-scan-btn');

    // Certificate / Customize Modal Elements
    const certModal = document.getElementById('certificate-modal');
    const closeCertModalBtn = document.getElementById('close-modal-btn');
    const downloadPosterBtn = document.getElementById('download-poster-btn');
    const shareMockBtn = document.getElementById('share-mock-btn');
    const toastMessage = document.getElementById('toast-message');

    // Poster fields
    const posterRecipientName = document.getElementById('poster-recipient-name');
    const posterRecipientDept = document.getElementById('poster-recipient-dept');
    const posterBadgeTitle = document.getElementById('poster-badge-title');
    const posterCongratulationsMsg = document.getElementById('poster-congratulations-msg');
    const posterStatRating = document.getElementById('poster-stat-rating');
    const posterStatProblems = document.getElementById('poster-stat-problems');
    const posterStatCf = document.getElementById('poster-stat-cf');
    const posterDate = document.getElementById('poster-date');

    // Certificate custom inputs
    const customNameInput = document.getElementById('custom-name-input');
    const customMsgInput = document.getElementById('custom-msg-input');
    const customRatingInput = document.getElementById('custom-rating-input');
    const customSolvedInput = document.getElementById('custom-solved-input');

    // App State
    let currentFilter = 'all';
    let currentSort = 'lc-rating-desc';
    let searchQuery = '';

    // Initialize Roster UI
    initializeStats();
    initializeDepartmentBattleground();
    initializeDuelSelectors();
    renderGrid();

    // -------------------------------------------------------------
    // Core Layout Functions
    // -------------------------------------------------------------
    
    function getGradientForName(name) {
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }
        const h1 = Math.abs(hash % 360);
        const h2 = (h1 + 60) % 360;
        return `linear-gradient(135deg, hsl(${h1}, 70%, 45%), hsl(${h2}, 60%, 30%))`;
    }

    function initializeStats() {
        statTotalCoders.textContent = roster.length;
        
        let peakRating = 0;
        let totalRepos = 0;
        roster.forEach(c => {
            if (c.leetcodeRating > peakRating) peakRating = c.leetcodeRating;
            totalRepos += c.githubRepos;
        });
        
        statPeakRating.textContent = peakRating;
        statTotalRepos.textContent = totalRepos;
        statActiveDuelists.textContent = roster.filter(c => c.leetcodeRating > 0 || c.codeforcesRating > 0).length;
    }

    function initializeDepartmentBattleground() {
        // Calculate departmental rating averages
        const depts = ["AIDS", "AIML", "CS", "CSBS", "CSE", "ECE", "IT", "VLSI"];
        const deptStats = depts.map(d => {
            const members = roster.filter(c => c.dept === d);
            const totalRating = members.reduce((sum, c) => sum + c.leetcodeRating, 0);
            const avgRating = members.length > 0 ? Math.round(totalRating / members.length) : 0;
            return {
                name: d,
                avgRating,
                memberCount: members.length
            };
        });

        // Sort departments by average rating
        deptStats.sort((a, b) => b.avgRating - a.avgRating);
        const maxAvgRating = deptStats[0].avgRating;

        deptMetricsContainer.innerHTML = '';
        deptStats.forEach(d => {
            const barPercentage = maxAvgRating > 0 ? (d.avgRating / maxAvgRating) * 100 : 0;
            const card = document.createElement('div');
            card.className = 'dept-card';
            card.innerHTML = `
                <div class="dept-header">
                    <span class="dept-name">${d.name}</span>
                    <span class="dept-avg-rating"><i class="fa-solid fa-code"></i> ${d.avgRating} Avg</span>
                </div>
                <div class="dept-progress-container">
                    <div class="dept-progress-bar" style="width: 0%;" data-width="${barPercentage}%"></div>
                </div>
                <div class="dept-members-count">${d.memberCount} active coders</div>
            `;
            deptMetricsContainer.appendChild(card);
        });

        // Trigger progress bar animations shortly after loading
        setTimeout(() => {
            document.querySelectorAll('.dept-progress-bar').forEach(bar => {
                bar.style.width = bar.getAttribute('data-width');
            });
        }, 300);
    }

    function initializeDuelSelectors() {
        // Sort students alphabetically for dropdowns
        const sortedFighters = [...roster].sort((a, b) => a.name.localeCompare(b.name));
        
        fighterASelect.innerHTML = '';
        fighterBSelect.innerHTML = '';

        sortedFighters.forEach(c => {
            const optA = document.createElement('option');
            optA.value = c.name;
            optA.textContent = `${c.name} (${c.dept})`;
            
            const optB = document.createElement('option');
            optB.value = c.name;
            optB.textContent = `${c.name} (${c.dept})`;

            fighterASelect.appendChild(optA);
            fighterBSelect.appendChild(optB);
        });

        // Select different defaults
        if (fighterBSelect.options.length > 1) {
            fighterBSelect.selectedIndex = 1;
        }
    }

    // Render Grid
    function renderGrid() {
        let filtered = roster.filter(c => {
            const matchesSearch = c.name.toLowerCase().includes(searchQuery) ||
                                  c.dept.toLowerCase().includes(searchQuery) ||
                                  (c.leetcode_username && c.leetcode_username.toLowerCase().includes(searchQuery)) ||
                                  (c.github_username && c.github_username.toLowerCase().includes(searchQuery));
            if (!matchesSearch) return false;

            if (currentFilter !== 'all') {
                return c.dept === currentFilter;
            }
            return true;
        });

        // Sort data
        filtered.sort((a, b) => {
            if (currentSort === 'lc-rating-desc') return b.leetcodeRating - a.leetcodeRating;
            if (currentSort === 'cf-rating-desc') return b.codeforcesRating - a.codeforcesRating;
            if (currentSort === 'gh-repos-desc') return b.githubRepos - a.githubRepos;
            if (currentSort === 'name-asc') return a.name.localeCompare(b.name);
            return 0;
        });

        gridContainer.innerHTML = '';
        
        if (filtered.length === 0) {
            gridContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-user-slash"></i>
                    <h3>No Coders Found</h3>
                    <p>No profiles match the filter options.</p>
                </div>
            `;
            return;
        }

        filtered.forEach(c => {
            const card = document.createElement('div');
            card.className = 'knight-card';
            
            // Extra badges
            let badgesHtml = '';
            if (c.codechef_stars) {
                badgesHtml += `<span class="extra-badge codechef"><i class="fa-solid fa-star"></i> CodeChef ${c.codechef_stars}</span>`;
            }
            if (c.codeforces_rank) {
                badgesHtml += `<span class="extra-badge codeforces"><i class="fa-solid fa-chart-line"></i> CF ${c.codeforces_rank}</span>`;
            }

            const cleanQuote = `GitHub: @${c.github_username} | Repos: ${c.github_repos} | Solved solved challenges across platforms.`;
            
            const isGuardian = c.role.toLowerCase().includes('guardian');
            const roleClass = isGuardian ? 'role-guardian' : (c.leetcodeRating >= 1850 ? 'role-knight' : 'role-specialist');
            const iconClass = isGuardian ? 'fa-solid fa-crown' : (c.leetcodeRating >= 1850 ? 'fa-solid fa-shield-halved' : 'fa-solid fa-code');

            card.innerHTML = `
                <div class="card-header">
                    <div class="card-title-area">
                        <h3 class="card-name">${c.name}</h3>
                        <span class="card-tagline">Dept: ${c.dept} | Sec: ${c.sec}</span>
                    </div>
                    <div class="badge-wrapper ${roleClass}" title="${c.role}">
                        <i class="${iconClass}"></i>
                    </div>
                </div>

                <div class="card-stats">
                    <div class="stat-pill highlight">
                        <span class="pill-num">${c.leetcode_rating}</span>
                        <span class="pill-lbl">LeetCode</span>
                    </div>
                    <div class="stat-pill">
                        <span class="pill-num">${c.github_repos}</span>
                        <span class="pill-lbl">Git Repos</span>
                    </div>
                </div>

                <blockquote class="card-quote">
                    ${cleanQuote}
                </blockquote>

                ${badgesHtml ? `<div class="extra-badges">${badgesHtml}</div>` : ''}

                <div class="card-footer">
                    <button class="card-btn btn-secondary scan-profile-btn" data-name="${c.name}">
                        <i class="fa-solid fa-terminal"></i> Scan Profile
                    </button>
                    <button class="card-btn btn-primary celebrate-btn" data-name="${c.name}">
                        <i class="fa-solid fa-award"></i> Certificate
                    </button>
                </div>
            `;
            
            gridContainer.appendChild(card);
        });

        // Re-attach listeners
        document.querySelectorAll('.celebrate-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const name = btn.getAttribute('data-name');
                const profile = roster.find(c => c.name === name);
                if (profile) openCertificateModal(profile);
            });
        });

        document.querySelectorAll('.scan-profile-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const name = btn.getAttribute('data-name');
                const profile = roster.find(c => c.name === name);
                if (profile) openTerminalScanner(profile);
            });
        });
    }

    // -------------------------------------------------------------
    // Controls Event Handlers
    // -------------------------------------------------------------
    
    searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value.toLowerCase().trim();
        clearSearchBtn.style.display = searchQuery ? 'block' : 'none';
        renderGrid();
    });

    clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        searchQuery = '';
        clearSearchBtn.style.display = 'none';
        renderGrid();
    });

    sortSelect.addEventListener('change', (e) => {
        currentSort = e.target.value;
        renderGrid();
    });

    filterChips.forEach(chip => {
        chip.addEventListener('click', () => {
            filterChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            currentFilter = chip.getAttribute('data-filter');
            renderGrid();
        });
    });

    // -------------------------------------------------------------
    // Code Duel Logic
    // -------------------------------------------------------------
    
    initiateDuelBtn.addEventListener('click', () => {
        const nameA = fighterASelect.value;
        const nameB = fighterBSelect.value;

        if (nameA === nameB) {
            alert("A coder cannot duel themselves! Please select two different coders.");
            return;
        }

        const coderA = roster.find(c => c.name === nameA);
        const coderB = roster.find(c => c.name === nameB);

        if (!coderA || !coderB) return;

        // Reveal board
        duelBoard.classList.remove('hidden');

        // Setup Names and Avatars
        duelNameA.textContent = coderA.name;
        duelDeptA.textContent = coderA.dept;
        duelAvatarA.textContent = coderA.name[0];
        duelAvatarA.style.background = getGradientForName(coderA.name);

        duelNameB.textContent = coderB.name;
        duelDeptB.textContent = coderB.dept;
        duelAvatarB.textContent = coderB.name[0];
        duelAvatarB.style.background = getGradientForName(coderB.name);

        // Populate Table stats
        duelValLcA.textContent = coderA.leetcode_rating;
        duelValLcB.textContent = coderB.leetcode_rating;
        
        duelValSolvedA.textContent = coderA.solved_count;
        duelValSolvedB.textContent = coderB.solved_count;
        
        duelValCfA.textContent = coderA.codeforces_rating;
        duelValCfB.textContent = coderB.codeforces_rating;
        
        duelValGhA.textContent = coderA.github_repos;
        duelValGhB.textContent = coderB.github_repos;

        // Calculate Duel Winner classes
        compareDuelMetric(coderA.leetcodeRating, coderB.leetcodeRating, duelValLcA, duelValLcB);
        compareDuelMetric(coderA.solvedCount, coderB.solvedCount, duelValSolvedA, duelValSolvedB);
        compareDuelMetric(coderA.codeforcesRating, coderB.codeforcesRating, duelValCfA, duelValCfB);
        compareDuelMetric(coderA.githubRepos, coderB.githubRepos, duelValGhA, duelValGhB);

        // Compute overall Coding Power Scores (Weighted comparison)
        const scoreA = (coderA.leetcodeRating * 0.4) + (coderA.solvedCount * 0.2) + (coderA.codeforcesRating * 0.3) + (coderA.githubRepos * 10 * 0.1);
        const scoreB = (coderB.leetcodeRating * 0.4) + (coderB.solvedCount * 0.2) + (coderB.codeforcesRating * 0.3) + (coderB.githubRepos * 10 * 0.1);

        // Animate health bars relative to combat scores
        healthBarA.style.width = '0%';
        healthBarB.style.width = '0%';

        setTimeout(() => {
            if (scoreA > scoreB) {
                healthBarA.style.width = '100%';
                healthBarB.style.width = `${Math.max(25, Math.round((scoreB / scoreA) * 100))}%`;
            } else {
                healthBarB.style.width = '100%';
                healthBarA.style.width = `${Math.max(25, Math.round((scoreA / scoreB) * 100))}%`;
            }
        }, 100);

        // Smooth scroll to board
        duelBoard.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });

    function compareDuelMetric(valA, valB, elA, elB) {
        elA.className = 'duel-stat-val left';
        elB.className = 'duel-stat-val right';

        if (valA > valB) {
            elA.classList.add('winner');
            elB.classList.add('loser');
        } else if (valB > valA) {
            elB.classList.add('winner');
            elA.classList.add('loser');
        }
    }

    // -------------------------------------------------------------
    // Live Terminal Scanner Animation
    // -------------------------------------------------------------
    
    function openTerminalScanner(profile) {
        scanModal.classList.add('open');
        terminalScanResult.classList.add('hidden');
        terminalConsole.innerHTML = '';
        document.body.style.overflow = 'hidden';

        const logs = [
            { text: `[SYSTEM] Initiating handshake with CIT servers...`, type: 'info' },
            { text: `[SYSTEM] Handshake OK (node-cit-2026)`, type: 'success' },
            { text: `[INFO] Decrypting database keys for user ID: ${profile.leetcode_username}...`, type: 'info' },
            { text: `[INFO] Querying LeetCode GraphQL API endpoint...`, type: 'info' },
            { text: `[SUCCESS] LeetCode profile decrypted. Rating: ${profile.leetcode_rating}`, type: 'success' },
            { text: `[INFO] Requesting Codeforces rank info for user: ${profile.codeforces_username}...`, type: 'info' },
            { text: `[SUCCESS] Codeforces rating resolved: ${profile.codeforces_rating} (${profile.codeforces_rank})`, type: 'success' },
            { text: `[INFO] Contacting GitHub API v3 REST payload...`, type: 'info' },
            { text: `[SUCCESS] Public Repositories discovered: ${profile.github_repos}`, type: 'success' },
            { text: `[INFO] Compiling cumulative departmental ranking indices...`, type: 'info' },
            { text: `[INFO] CIT Decryptor successfully generated profile card.`, type: 'success' }
        ];

        let lineIdx = 0;
        function printNextLine() {
            if (lineIdx < logs.length) {
                const log = logs[lineIdx];
                const div = document.createElement('div');
                div.className = `term-log ${log.type}`;
                div.textContent = log.text;
                terminalConsole.appendChild(div);
                
                // Keep scrolled to bottom
                terminalConsole.scrollTop = terminalConsole.scrollHeight;

                lineIdx++;
                setTimeout(printNextLine, 200 + randomDelay());
            } else {
                // Done printing, display decoded card result
                revealScanResult(profile);
            }
        }

        // Slight random variation in terminal speed
        function randomDelay() {
            return Math.floor(Math.random() * 200);
        }

        // Start typing simulation
        setTimeout(printNextLine, 300);
    }

    function revealScanResult(profile) {
        const isGuardian = profile.role.toLowerCase().includes('guardian');
        const roleColor = isGuardian ? '#ef4444' : '#00ff88';
        const roleBg = isGuardian ? 'rgba(239, 68, 68, 0.1)' : 'rgba(0, 255, 136, 0.1)';
        const roleBorder = isGuardian ? 'rgba(239, 68, 68, 0.25)' : 'rgba(0, 255, 136, 0.25)';

        terminalScanResult.innerHTML = `
            <div class="result-card-inner">
                <span class="result-role" style="color: ${roleColor}; background: ${roleBg}; border-color: ${roleBorder};">${profile.role}</span>
                <h2 style="color: #ffffff; margin-bottom: 4px;">${profile.name}</h2>
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 20px;">
                    Department of ${profile.dept} | Section ${profile.sec}
                </p>

                <div class="result-stats-grid">
                    <div class="result-stat-pill">
                        <span class="result-stat-val">${profile.leetcode_rating}</span>
                        <span class="result-stat-lbl">LeetCode</span>
                    </div>
                    <div class="result-stat-pill">
                        <span class="result-stat-val">${profile.codeforces_rating}</span>
                        <span class="result-stat-lbl">Codeforces</span>
                    </div>
                    <div class="result-stat-pill">
                        <span class="result-stat-val">${profile.github_repos}</span>
                        <span class="result-stat-lbl">Git Repos</span>
                    </div>
                </div>

                <div class="action-buttons-group">
                    <a href="https://leetcode.com/${profile.leetcode_username}" target="_blank" class="action-btn share-btn" style="font-size: 0.8rem; padding: 10px;">
                        <i class="fa-solid fa-code"></i> LeetCode
                    </a>
                    <a href="https://github.com/${profile.github_username}" target="_blank" class="action-btn share-btn" style="font-size: 0.8rem; padding: 10px;">
                        <i class="fa-brands fa-github"></i> GitHub
                    </a>
                </div>

                <button class="close-result-btn" id="close-result-card-btn">Close decrypted scan</button>
            </div>
        `;

        terminalScanResult.classList.remove('hidden');

        document.getElementById('close-result-card-btn').addEventListener('click', closeTerminalScanner);
    }

    function closeTerminalScanner() {
        scanModal.classList.remove('open');
        document.body.style.overflow = 'auto';
    }

    closeScanBtn.addEventListener('click', closeTerminalScanner);
    scanModal.querySelector('.modal-overlay').addEventListener('click', closeTerminalScanner);

    // -------------------------------------------------------------
    // Certificate Card Popup & Personalizer
    // -------------------------------------------------------------
    
    function openCertificateModal(profile) {
        customNameInput.value = profile.name;
        customRatingInput.value = profile.leetcode_rating;
        customSolvedInput.value = profile.solved_count;
        
        let customMessage = `For outstanding placement readiness and solving ${profile.solved_count} challenges across platforms (LeetCode & Codeforces), demonstrating exceptional credentials in DSA.`;
        customMsgInput.value = customMessage;

        updatePosterPreview(profile.dept);

        certModal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function updatePosterPreview(department = 'COMPUTER SCIENCE') {
        posterRecipientName.textContent = customNameInput.value.trim() || "Student Name";
        posterRecipientDept.textContent = `DEPARTMENT OF ${department.toUpperCase()}`;
        posterStatRating.textContent = customRatingInput.value.trim() || "1850+";
        posterStatProblems.textContent = customSolvedInput.value.trim() || "500+";
        posterCongratulationsMsg.textContent = customMsgInput.value.trim();
        
        const r = parseInt(customRatingInput.value);
        if (!isNaN(r) && r >= 2150) {
            posterBadgeTitle.textContent = "LEETCODE GUARDIAN";
            document.querySelector('.poster-gold-shield').style.color = '#ef4444';
            posterStatCf.textContent = "Guardian";
        } else {
            posterBadgeTitle.textContent = "LEETCODE KNIGHT";
            document.querySelector('.poster-gold-shield').style.color = '#f59e0b';
            posterStatCf.textContent = "Knight";
        }
        
        const options = { month: 'long', year: 'numeric' };
        posterDate.textContent = new Date().toLocaleDateString('en-US', options);
    }

    customNameInput.addEventListener('input', () => updatePosterPreview());
    customMsgInput.addEventListener('input', () => updatePosterPreview());
    customRatingInput.addEventListener('input', () => updatePosterPreview());
    customSolvedInput.addEventListener('input', () => updatePosterPreview());

    function closeCertModal() {
        certModal.classList.remove('open');
        document.body.style.overflow = 'auto';
    }

    closeCertModalBtn.addEventListener('click', closeCertModal);
    certModal.querySelector('.modal-overlay').addEventListener('click', closeCertModal);

    downloadPosterBtn.addEventListener('click', () => {
        const posterEl = document.getElementById('achievement-poster');
        downloadPosterBtn.disabled = true;
        downloadPosterBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Exporting...`;

        setTimeout(() => {
            html2canvas(posterEl, {
                scale: 2,
                useCORS: true,
                backgroundColor: null,
                logging: false
            }).then(canvas => {
                const imgData = canvas.toDataURL('image/png');
                const link = document.createElement('a');
                const slugName = (customNameInput.value || 'achievement').trim().toLowerCase().replace(/\s+/g, '-');
                link.download = `cit-coder-${slugName}.png`;
                link.href = imgData;
                link.click();

                downloadPosterBtn.disabled = false;
                downloadPosterBtn.innerHTML = `<i class="fa-solid fa-download"></i> Download PNG`;
            }).catch(err => {
                console.error("Canvas render error: ", err);
                downloadPosterBtn.disabled = false;
                downloadPosterBtn.innerHTML = `<i class="fa-solid fa-download"></i> Download PNG`;
            });
        }, 100);
    });

    shareMockBtn.addEventListener('click', () => {
        const nameParam = encodeURIComponent(customNameInput.value.trim());
        const mockUrl = `${window.location.origin}${window.location.pathname}?celebrate=${nameParam}`;
        
        navigator.clipboard.writeText(mockUrl).then(() => {
            toastMessage.classList.add('show');
            setTimeout(() => toastMessage.classList.remove('show'), 3000);
        }).catch(err => console.error('Link copy failed: ', err));
    });
});
