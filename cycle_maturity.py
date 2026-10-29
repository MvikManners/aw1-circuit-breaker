import os
import sys
from datetime import datetime
from flask_mail import Message

# Architectural Law: Locating the Shield Reservoir
project_home = u'/home/LavetoLab'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from app import app, db, mail, SovereignLedger, SystemUpdate

def send_diamond_declaration(member):
    """
    Transmits the Sovereign Restoration Declaration via the Mail Engine.
    """
    try:
        msg = Message(
            subject="NOTICE: UNSEALED SOVEREIGN CAPITAL (Doc 58 // Diamond Status)",
            recipients=[member.member_email]
        )
        msg.body = f"""
Dear Sovereign Partner,

The Gospel OS has officially verified your 24-month purification cycle within the Shield Reservoir. 

By maintaining absolute discipline and prioritizing the restoration of your automotive asset, you have successfully transitioned from GREEN STATUS to 💎 DIAMOND STATUS.

WHAT THIS MEANS FOR YOUR ACCOUNT:
1. Maturity Gate Unlocked: Per Covenant Clause 5.2, you are no longer restricted to 'Restoration-Only' capital. 
2. Sovereign Trust: Your node is now recognized as a 'Proven Asset' within the Laveto Network.
3. Expanded Liquidity: You may now apply for capital minting for External purposes.

ARCHITECT’S NOTE:
This status is a testament to your commitment to the System Restoration philosophy. You have proven that you can manage capital with the precision of an engineer and the discipline of a sovereign.

In Restoration,

Vela
Managing Director // Laveto Pty Ltd
Gaborone Command
        """
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Mail Engine Error for {member.vin_dna}: {str(e)}")
        return False

def increment_maturity_cycle():
    """
    The Purification Cycle: Advances months_in_green and triggers Diamond Declarations.
    """
    with app.app_context():
        # Only advance members not flagged with 'Malware' status
        active_members = SovereignLedger.query.filter(
            SovereignLedger.status.notin_(['Malware', 'Defaulter', 'Suspended'])
        ).all()
        
        count = 0
        diamond_triggers = 0
        
        for member in active_members:
            # Increment the discipline counter
            member.months_in_green = (member.months_in_green or 0) + 1
            
            # TRIGGER: Check if the node just reached Diamond Status (24 months)
            if member.months_in_green == 24 and member.member_email:
                if send_diamond_declaration(member):
                    diamond_triggers += 1
            
            count += 1
            
        # Log the system update to the Command Wall
        log_entry = SystemUpdate(
            component="GOSPEL OS MATURITY ENGINE",
            description=f"Cycle Complete. {count} members advanced. {diamond_triggers} Diamond Declarations issued."
        )
        
        db.session.add(log_entry)
        db.session.commit()
        print(f"[{datetime.utcnow()}] Cycle Successful: {count} updated, {diamond_triggers} Diamond(s) notified.")

if __name__ == "__main__":
    increment_maturity_cycle()