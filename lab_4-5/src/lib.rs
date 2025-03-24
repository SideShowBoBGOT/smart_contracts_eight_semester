// Find all our documentation at https://docs.near.org

type LoyaltySystemPoint = u32;

#[near_sdk::near(serializers = [borsh])]
struct ParticipantInfo {
    points: LoyaltySystemPoint
}

enum LoyaltySystemStoragePrefix {
    Participants
}

// Define the contract structure
#[near_sdk::near(contract_state)]
pub struct LoyaltySystem {
    
    owner_id: near_sdk::AccountId,
    participants: near_sdk::store::LookupMap<near_sdk::AccountId, ParticipantInfo>
}

// Define the default, which automatically initializes the contract
impl Default for LoyaltySystem {
    fn default() -> Self {
        Self {
            owner_id: near_sdk::env::predecessor_account_id(),
            participants: near_sdk::store::LookupMap::new(LoyaltySystemStoragePrefix::Participants as u8)
        }
    }
}

const YOCTO_NEAR_PER_TOKEN: u128 = near_sdk::NearToken::from_near(1).as_yoctonear();

#[near_sdk::near]
impl LoyaltySystem {

    #[payable]
    pub fn award_points(&mut self) -> near_sdk::Promise {
        let deposit = near_sdk::env::attached_deposit().as_yoctonear();
        near_sdk::require!(deposit >= YOCTO_NEAR_PER_TOKEN);

        let participant_id = near_sdk::env::predecessor_account_id();
        let tokens_to_award = (deposit / YOCTO_NEAR_PER_TOKEN) as LoyaltySystemPoint;

        if !self.participants.contains_key(&participant_id) {
            self.participants.set(participant_id.clone(), Some(
                ParticipantInfo {points: tokens_to_award}
            ));
        } else {
            let participant_info = self.participants.get_mut(&participant_id).unwrap();
            let result_points = participant_info.points.checked_add(tokens_to_award);
            near_sdk::require!(result_points.is_some());
            participant_info.points = result_points.unwrap();
        }

        let near_tokens_to_return = deposit - YOCTO_NEAR_PER_TOKEN * (tokens_to_award as u128);
        near_sdk::Promise::new(participant_id).transfer(near_sdk::NearToken::from_yoctonear(near_tokens_to_return))
    }

    pub fn redeem_points(&mut self, points_to_spend: u32) -> String {
        let participant_id = near_sdk::env::predecessor_account_id();
        let participant_info = self.participants.get_mut(&participant_id);
        near_sdk::require!(participant_info.is_some());
        let participant_info = participant_info.unwrap();
        
        near_sdk::require!(participant_info.points >= points_to_spend);
        participant_info.points -= points_to_spend;

        points_to_spend.to_string()
    }
}