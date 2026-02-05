// ═══════════════════════════════════════════════════════════════════
// FLUXION LICENSE GENERATOR
// Tool ufficiale per generare licenze Ed25519 firmate
// 
// ⚠️  IMPORTANTE: Questo tool usa la CHIAVE PRIVATA
//    Tenere in luogo sicuro e non condividere!
// ═══════════════════════════════════════════════════════════════════

use anyhow::{Context, Result};
use chrono::{Duration, Utc};
use clap::{Parser, Subcommand};
use colored::Colorize;
use ed25519_dalek::{SigningKey, Signature, Signer, Verifier};
use rand::rngs::OsRng;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::fs;
use std::path::Path;

// ═══════════════════════════════════════════════════════════════════
// TYPES (devono matchare con il codice principale FLUXION)
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize, Deserialize)]
struct FluxionLicense {
    version: String,
    license_id: String,
    tier: LicenseTier,
    issued_at: String,
    expires_at: Option<String>,
    hardware_fingerprint: String,
    licensee_name: Option<String>,
    licensee_email: Option<String>,
    enabled_verticals: Vec<String>,
    max_operators: i32,
    features: LicenseFeatures,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
enum LicenseTier {
    Trial,
    Base,
    Pro,
    Enterprise,
}

impl LicenseTier {
    fn as_str(&self) -> &'static str {
        match self {
            LicenseTier::Trial => "trial",
            LicenseTier::Base => "base",
            LicenseTier::Pro => "pro",
            LicenseTier::Enterprise => "enterprise",
        }
    }
    
    fn display_name(&self) -> &'static str {
        match self {
            LicenseTier::Trial => "Trial",
            LicenseTier::Base => "FLUXION Base",
            LicenseTier::Pro => "FLUXION Pro",
            LicenseTier::Enterprise => "FLUXION Enterprise",
        }
    }
    
    fn price(&self) -> i32 {
        match self {
            LicenseTier::Trial => 0,
            LicenseTier::Base => 199,
            LicenseTier::Pro => 399,
            LicenseTier::Enterprise => 799,
        }
    }
    
    fn default_verticals(&self) -> Vec<String> {
        match self {
            LicenseTier::Trial => vec![
                "odontoiatrica".to_string(),
                "fisioterapia".to_string(),
                "estetica".to_string(),
                "parrucchiere".to_string(),
                "veicoli".to_string(),
                "carrozzeria".to_string(),
                "medica".to_string(),
                "fitness".to_string(),
            ],
            LicenseTier::Base => vec![], // 1 verticale a scelta
            LicenseTier::Pro => vec![],  // 3 verticali a scelta
            LicenseTier::Enterprise => vec![ // Tutte
                "odontoiatrica".to_string(),
                "fisioterapia".to_string(),
                "estetica".to_string(),
                "parrucchiere".to_string(),
                "veicoli".to_string(),
                "carrozzeria".to_string(),
                "medica".to_string(),
                "fitness".to_string(),
            ],
        }
    }
}

impl std::str::FromStr for LicenseTier {
    type Err = String;
    
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "trial" => Ok(LicenseTier::Trial),
            "base" => Ok(LicenseTier::Base),
            "pro" => Ok(LicenseTier::Pro),
            "enterprise" => Ok(LicenseTier::Enterprise),
            _ => Err(format!("Tier non valido: {}", s)),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct LicenseFeatures {
    voice_agent: bool,
    whatsapp_ai: bool,
    rag_chat: bool,
    fatturazione_pa: bool,
    loyalty_advanced: bool,
    api_access: bool,
    max_verticals: i32,
}

impl LicenseFeatures {
    fn for_tier(tier: &LicenseTier) -> Self {
        match tier {
            LicenseTier::Trial => Self {
                voice_agent: true,
                whatsapp_ai: true,
                rag_chat: true,
                fatturazione_pa: true,
                loyalty_advanced: true,
                api_access: true,
                max_verticals: 99,
            },
            LicenseTier::Base => Self {
                voice_agent: false,
                whatsapp_ai: false,
                rag_chat: false,
                fatturazione_pa: true,
                loyalty_advanced: false,
                api_access: false,
                max_verticals: 1,
            },
            LicenseTier::Pro => Self {
                voice_agent: true,
                whatsapp_ai: true,
                rag_chat: true,
                fatturazione_pa: true,
                loyalty_advanced: true,
                api_access: false,
                max_verticals: 3,
            },
            LicenseTier::Enterprise => Self {
                voice_agent: true,
                whatsapp_ai: true,
                rag_chat: true,
                fatturazione_pa: true,
                loyalty_advanced: true,
                api_access: true,
                max_verticals: 0, // Illimitato
            },
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct SignedLicense {
    license: FluxionLicense,
    signature: String,
}

// ═══════════════════════════════════════════════════════════════════
// KEY MANAGEMENT
// ═══════════════════════════════════════════════════════════════════

struct KeyPair {
    signing_key: SigningKey,
}

impl KeyPair {
    fn generate() -> Self {
        let mut csprng = OsRng;
        let signing_key = SigningKey::generate(&mut csprng);
        Self { signing_key }
    }
    
    fn from_private_key_hex(hex_key: &str) -> Result<Self> {
        let bytes = hex::decode(hex_key)?;
        let key_bytes: [u8; 32] = bytes.try_into()
            .map_err(|_| anyhow::anyhow!("Chiave privata deve essere 32 byte"))?;
        let signing_key = SigningKey::from_bytes(&key_bytes);
        Ok(Self { signing_key })
    }
    
    fn private_key_hex(&self) -> String {
        hex::encode(self.signing_key.to_bytes())
    }
    
    fn public_key_hex(&self) -> String {
        hex::encode(self.signing_key.verifying_key().to_bytes())
    }
    
    fn save_to_file(&self, path: &str) -> Result<()> {
        let data = serde_json::json!({
            "private_key": self.private_key_hex(),
            "public_key": self.public_key_hex(),
            "generated_at": Utc::now().to_rfc3339(),
        });
        fs::write(path, serde_json::to_string_pretty(&data)?)?;
        Ok(())
    }
    
    fn load_from_file(path: &str) -> Result<Self> {
        let content = fs::read_to_string(path)?;
        let data: serde_json::Value = serde_json::from_str(&content)?;
        let private_key = data["private_key"].as_str()
            .context("Chiave privata non trovata nel file")?;
        Self::from_private_key_hex(private_key)
    }
}

// ═══════════════════════════════════════════════════════════════════
// LICENSE GENERATION
// ═══════════════════════════════════════════════════════════════════

fn generate_license(
    keypair: &KeyPair,
    tier: LicenseTier,
    fingerprint: &str,
    licensee_name: Option<String>,
    licensee_email: Option<String>,
    enabled_verticals: Option<Vec<String>>,
    days_valid: Option<i64>,
) -> Result<SignedLicense> {
    let license_id = format!("FLX-{}-{}", 
        tier.as_str().to_uppercase(),
        generate_short_id()
    );
    
    let now = Utc::now();
    let expires_at = days_valid.map(|days| (now + Duration::days(days)).to_rfc3339());
    
    // Se non specificate verticali, usa quelle di default del tier
    let verticals = enabled_verticals.unwrap_or_else(|| tier.default_verticals());
    
    let license = FluxionLicense {
        version: "1.0".to_string(),
        license_id,
        tier: tier.clone(),
        issued_at: now.to_rfc3339(),
        expires_at,
        hardware_fingerprint: fingerprint.to_string(),
        licensee_name,
        licensee_email,
        enabled_verticals: verticals,
        max_operators: 0, // Illimitato per ora
        features: LicenseFeatures::for_tier(&tier),
    };
    
    // Firma la licenza
    let license_json = serde_json::to_string(&license)?;
    let signature = keypair.signing_key.sign(license_json.as_bytes());
    let signature_b64 = base64::encode(signature.to_bytes());
    
    Ok(SignedLicense {
        license,
        signature: signature_b64,
    })
}

fn generate_short_id() -> String {
    use rand::Rng;
    const CHARSET: &[u8] = b"ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    let mut rng = OsRng;
    (0..8)
        .map(|_| CHARSET[rng.gen_range(0..CHARSET.len())] as char)
        .collect()
}

fn verify_license(keypair: &KeyPair, signed_license: &SignedLicense) -> Result<bool> {
    let license_json = serde_json::to_string(&signed_license.license)?;
    let signature_bytes = base64::decode(&signed_license.signature)?;
    let signature = Signature::from_bytes(
        &signature_bytes.try_into().map_err(|_| anyhow::anyhow!("Firma invalida"))?
    );
    
    match keypair.signing_key.verifying_key().verify(license_json.as_bytes(), &signature) {
        Ok(_) => Ok(true),
        Err(_) => Ok(false),
    }
}

// ═══════════════════════════════════════════════════════════════════
// CLI
// ═══════════════════════════════════════════════════════════════════

#[derive(Parser)]
#[command(name = "FLUXION License Generator")]
#[command(about = "Genera licenze Ed25519 firmate per FLUXION")]
#[command(version = "1.0.0")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Genera un nuovo keypair (da fare una sola volta)
    Init {
        /// Path dove salvare il keypair
        #[arg(short, long, default_value = "fluxion-keypair.json")]
        output: String,
    },
    
    /// Genera una nuova licenza
    Generate {
        /// Path del keypair
        #[arg(short, long, default_value = "fluxion-keypair.json")]
        keypair: String,
        
        /// Tier licenza (trial, base, pro, enterprise)
        #[arg(short, long)]
        tier: String,
        
        /// Hardware fingerprint del cliente
        #[arg(short, long)]
        fingerprint: String,
        
        /// Nome licenziatario
        #[arg(short, long)]
        name: Option<String>,
        
        /// Email licenziatario
        #[arg(short, long)]
        email: Option<String>,
        
        /// Verticali abilitate (separate da virgola)
        #[arg(short, long)]
        verticals: Option<String>,
        
        /// Giorni di validità (omesso = lifetime)
        #[arg(short, long)]
        days: Option<i64>,
        
        /// Path output licenza
        #[arg(short, long, default_value = "license.json")]
        output: String,
    },
    
    /// Verifica una licenza esistente
    Verify {
        /// Path del keypair
        #[arg(short, long, default_value = "fluxion-keypair.json")]
        keypair: String,
        
        /// Path della licenza da verificare
        #[arg(short, long)]
        license: String,
    },
    
    /// Mostra informazioni su una licenza
    Info {
        /// Path della licenza
        #[arg(short, long)]
        license: String,
    },
    
    /// Genera fingerprint di questa macchina (per test)
    Fingerprint,
}

// ═══════════════════════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════════════════════

fn main() -> Result<()> {
    let cli = Cli::parse();
    
    match cli.command {
        Commands::Init { output } => {
            println!("{}", "🔐 Generazione nuovo keypair Ed25519...".cyan().bold());
            
            let keypair = KeyPair::generate();
            keypair.save_to_file(&output)?;
            
            println!("{}", "✅ Keypair generato con successo!".green().bold());
            println!("\n{}", "⚠️  IMPORTANTE:".yellow().bold());
            println!("{}", "   - Conserva questo file in luogo SICURO".yellow());
            println!("{}", "   - Non condividere MAI la chiave privata".yellow());
            println!("{}", "   - Per sicurezza, conserva offline".yellow());
            println!("\nChiave pubblica da inserire in FLUXION:");
            println!("{}", keypair.public_key_hex().green());
            println!("\nFile salvato in: {}", output.green());
        }
        
        Commands::Generate { keypair, tier, fingerprint, name, email, verticals, days, output } => {
            println!("{}", "📝 Generazione licenza FLUXION...".cyan().bold());
            
            let kp = KeyPair::load_from_file(&keypair)?;
            let tier_enum = tier.parse::<LicenseTier>().map_err(|e| anyhow::anyhow!("Tier invalid: {}", e))?;
            
            let verticals_vec = verticals.map(|v| {
                v.split(',').map(|s| s.trim().to_string()).collect()
            });
            
            let signed_license = generate_license(
                &kp,
                tier_enum,
                &fingerprint,
                name,
                email,
                verticals_vec,
                days,
            )?;
            
            // Salva licenza
            fs::write(&output, serde_json::to_string_pretty(&signed_license)?)?;
            
            println!("{}", "✅ Licenza generata con successo!".green().bold());
            println!("\n📋 Dettagli:");
            println!("   ID: {}", signed_license.license.license_id.cyan());
            println!("   Tier: {}", signed_license.license.tier.display_name().cyan());
            println!("   Fingerprint: {}", signed_license.license.hardware_fingerprint.cyan());
            println!("   Scadenza: {}", 
                signed_license.license.expires_at.as_deref().unwrap_or("Lifetime (mai)").cyan()
            );
            println!("   Verticali: {}", signed_license.license.enabled_verticals.join(", ").cyan());
            println!("\n💾 File salvato in: {}", output.green());
            println!("\n{}", "📧 Invia questo file al cliente per l'attivazione.".yellow());
        }
        
        Commands::Verify { keypair, license } => {
            println!("{}", "🔍 Verifica licenza...".cyan().bold());
            
            let kp = KeyPair::load_from_file(&keypair)?;
            let license_content = fs::read_to_string(&license)?;
            let signed_license: SignedLicense = serde_json::from_str(&license_content)?;
            
            let valid = verify_license(&kp, &signed_license)?;
            
            if valid {
                println!("{}", "✅ Licenza VALIDA - Firma corretta".green().bold());
            } else {
                println!("{}", "❌ Licenza NON VALIDA - Firma scorretta".red().bold());
            }
        }
        
        Commands::Info { license } => {
            let license_content = fs::read_to_string(&license)?;
            let signed_license: SignedLicense = serde_json::from_str(&license_content)?;
            let l = &signed_license.license;
            
            println!("{}", "📋 Informazioni Licenza".cyan().bold());
            println!("═══════════════════════════════════════");
            println!("ID:           {}", l.license_id);
            println!("Versione:     {}", l.version);
            println!("Tier:         {}", l.tier.display_name());
            println!("Prezzo:       €{}", l.tier.price());
            println!("Rilasciata:   {}", l.issued_at);
            println!("Scadenza:     {}", l.expires_at.as_deref().unwrap_or("Lifetime"));
            println!("Fingerprint:  {}", l.hardware_fingerprint);
            println!("Nome:         {}", l.licensee_name.as_deref().unwrap_or("N/D"));
            println!("Email:        {}", l.licensee_email.as_deref().unwrap_or("N/D"));
            println!("Verticali:    {}", l.enabled_verticals.join(", "));
            println!("\nFunzionalità:");
            println!("  Voice Agent:     {}", if l.features.voice_agent { "✅".green() } else { "❌".red() });
            println!("  WhatsApp AI:     {}", if l.features.whatsapp_ai { "✅".green() } else { "❌".red() });
            println!("  RAG Chat:        {}", if l.features.rag_chat { "✅".green() } else { "❌".red() });
            println!("  Fatturazione PA: {}", if l.features.fatturazione_pa { "✅".green() } else { "❌".red() });
            println!("  Loyalty:         {}", if l.features.loyalty_advanced { "✅".green() } else { "❌".red() });
            println!("  API Access:      {}", if l.features.api_access { "✅".green() } else { "❌".red() });
            println!("\nFirma:        {}...", &signed_license.signature[..50]);
        }
        
        Commands::Fingerprint => {
            use sysinfo::System;
            
            let mut sys = System::new_all();
            sys.refresh_all();
            
            let hostname = System::host_name().unwrap_or_else(|| "unknown".to_string());
            let cpu_brand = sys.cpus().first()
                .map(|c| c.brand().to_string())
                .unwrap_or_else(|| "unknown".to_string());
            let total_memory = sys.total_memory();
            let system_name = System::name().unwrap_or_else(|| "unknown".to_string());
            
            let fingerprint_source = format!("{}:{}:{}:{}", hostname, cpu_brand, total_memory, system_name);
            let mut hasher = Sha256::new();
            hasher.update(fingerprint_source.as_bytes());
            let fingerprint = hex::encode(&hasher.finalize()[..16]);
            
            println!("{}", "🔐 Hardware Fingerprint".cyan().bold());
            println!("═══════════════════════════════════════");
            println!("Hostname:     {}", hostname);
            println!("CPU:          {}", cpu_brand);
            println!("RAM:          {} MB", total_memory);
            println!("OS:           {}", system_name);
            println!("\nFingerprint:  {}", fingerprint.green().bold());
            println!("\n{}", "Copia questo valore quando generi la licenza.".yellow());
        }
    }
    
    Ok(())
}
