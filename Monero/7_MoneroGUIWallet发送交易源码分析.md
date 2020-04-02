# Monero GUI Wallet发送交易源码分析

> 源码: https://github.com/monero-project/monero-gui

Monero GUI Wallet 使用了 QML技术



- `Transfer.qml`

  ```
  Rectangle {
      id: root
      signal paymentClicked(string address, string paymentId, string amount, int mixinCount,
                            int priority, string description)
      signal sweepUnmixableClicked()
      
      ......
      
       RowLayout {
            StandardButton {
                id: sendButton
                rightIcon: "qrc:///images/rightArrow.png"
                rightIconInactive: "qrc:///images/rightArrowInactive.png"
                Layout.topMargin: 4
                text: qsTr("Send") + translationManager.emptyString
                enabled: !sendButtonWarningBox.visible && !warningContent && addressLine.text && !paymentIdWarningBox.visible
                onClicked: {
                    console.log("Transfer: paymentClicked")
                    var priority = priorityModelV5.get(priorityDropdown.currentIndex).priority
                    console.log("priority: " + priority)
                    console.log("amount: " + amountLine.text)
                    addressLine.text = addressLine.text.trim()
                    setPaymentId(paymentIdLine.text.trim());
                    root.paymentClicked(addressLine.text, paymentIdLine.text, amountLine.text, root.mixin, priority, descriptionLine.text)
                }
            }
        }
  ```

- `main.qml`

  ```
  ....
  middlePanel.paymentClicked.connect(handlePayment);  //将Send按钮的点击事件与handlePayment绑定
  middlePanel.sweepUnmixableClicked.connect(handleSweepUnmixable);
  ....
  
  
  	// called on "transfer"
      function handlePayment(address, paymentId, amount, mixinCount, priority, description, createFile) {
          console.log("Creating transaction: ")
          console.log("\taddress: ", address,
                      ", payment_id: ", paymentId,
                      ", amount: ", amount,
                      ", mixins: ", mixinCount,
                      ", priority: ", priority,
                      ", description: ", description);
  
          var splashMsg = qsTr("Creating transaction...");
          splashMsg += appWindow.currentWallet.isLedger() ? qsTr("\n\nPlease check your hardware wallet –\nyour input may be required.") : "";
          showProcessingSplash(splashMsg);
  
          transactionDescription = description;
  
          // validate amount;
          if (amount !== "(all)") {
              var amountxmr = walletManager.amountFromString(amount);
              console.log("integer amount: ", amountxmr);
              console.log("integer unlocked", currentWallet.unlockedBalance())
              if (amountxmr <= 0) {
                  hideProcessingSplash()
                  informationPopup.title = qsTr("Error") + translationManager.emptyString;
                  informationPopup.text  = qsTr("Amount is wrong: expected number from %1 to %2")
                          .arg(walletManager.displayAmount(0))
                          .arg(walletManager.displayAmount(currentWallet.unlockedBalance()))
                          + translationManager.emptyString
  
                  informationPopup.icon  = StandardIcon.Critical
                  informationPopup.onCloseCallback = null
                  informationPopup.open()
                  return;
              } else if (amountxmr > currentWallet.unlockedBalance()) {
                  hideProcessingSplash()
                  informationPopup.title = qsTr("Error") + translationManager.emptyString;
                  informationPopup.text  = qsTr("Insufficient funds. Unlocked balance: %1")
                          .arg(walletManager.displayAmount(currentWallet.unlockedBalance()))
                          + translationManager.emptyString
  
                  informationPopup.icon  = StandardIcon.Critical
                  informationPopup.onCloseCallback = null
                  informationPopup.open()
                  return;
              }
          }
  
          if (amount === "(all)")
              currentWallet.createTransactionAllAsync(address, paymentId, mixinCount, priority);
          else
          	//调用 C++的函数进行异步创建交易(不阻塞, 会显示 "创建中..."遮挡页面), 当创建成功后会发送创建成功的信号
              currentWallet.createTransactionAsync(address, paymentId, amountxmr, mixinCount, priority);
      }
      
      
      //交易异步创建后,  响应C++发来的信号, 弹出对话框让用户确认
      function onTransactionCreated(pendingTransaction,address,paymentId,mixinCount){
          console.log("Transaction created");
          hideProcessingSplash();
          transaction = pendingTransaction;
          // validate address;
          if (transaction.status !== PendingTransaction.Status_Ok) {
              console.error("Can't create transaction: ", transaction.errorString);
              informationPopup.title = qsTr("Error") + translationManager.emptyString;
              if (currentWallet.connected() == Wallet.ConnectionStatus_WrongVersion)
                  informationPopup.text  = qsTr("Can't create transaction: Wrong daemon version: ") + transaction.errorString
              else
                  informationPopup.text  = qsTr("Can't create transaction: ") + transaction.errorString
              informationPopup.icon  = StandardIcon.Critical
              informationPopup.onCloseCallback = null
              informationPopup.open();
              // deleting transaction object, we don't want memleaks
              currentWallet.disposeTransaction(transaction);
  
          } else if (transaction.txCount == 0) {
              informationPopup.title = qsTr("Error") + translationManager.emptyString
              informationPopup.text  = qsTr("No unmixable outputs to sweep") + translationManager.emptyString
              informationPopup.icon = StandardIcon.Information
              informationPopup.onCloseCallback = null
              informationPopup.open()
              // deleting transaction object, we don't want memleaks
              currentWallet.disposeTransaction(transaction);
          } else {
              console.log("Transaction created, amount: " + walletManager.displayAmount(transaction.amount)
                      + ", fee: " + walletManager.displayAmount(transaction.fee));
  
              // here we show confirmation popup;
              transactionConfirmationPopup.title = qsTr("Please confirm transaction:\n") + translationManager.emptyString;
              transactionConfirmationPopup.text = "";
              transactionConfirmationPopup.text += (address === "" ? "" : (qsTr("Address: ") + address));
              transactionConfirmationPopup.text += (paymentId === "" ? "" : (qsTr("\nPayment ID: ") + paymentId));
              transactionConfirmationPopup.text +=  qsTr("\n\nAmount: ") + walletManager.displayAmount(transaction.amount);
              transactionConfirmationPopup.text +=  qsTr("\nFee: ") + walletManager.displayAmount(transaction.fee);
              transactionConfirmationPopup.text +=  qsTr("\nRingsize: ") + (mixinCount + 1);
              transactionConfirmationPopup.text +=  qsTr("\n\nNumber of transactions: ") + transaction.txCount
              transactionConfirmationPopup.text +=  (transactionDescription === "" ? "" : (qsTr("\nDescription: ") + transactionDescription))
              for (var i = 0; i < transaction.subaddrIndices.length; ++i){
                  transactionConfirmationPopup.text += qsTr("\nSpending address index: ") + transaction.subaddrIndices[i];
              }
  
              transactionConfirmationPopup.text += translationManager.emptyString;
              transactionConfirmationPopup.icon = StandardIcon.Question
              transactionConfirmationPopup.open()
          }
      }
  
  
  
  	//对交易进行确认
  // called after user confirms transaction
      function handleTransactionConfirmed(fileName) {
          // View only wallet - we save the tx
          if(viewOnly && saveTxDialog.fileUrl){
              // No file specified - abort
              if(!saveTxDialog.fileUrl) {
                  currentWallet.disposeTransaction(transaction)
                  return;
              }
  
              var path = walletManager.urlToLocalPath(saveTxDialog.fileUrl)
  
              // Store to file
              transaction.setFilename(path);
          }
  
          appWindow.showProcessingSplash(qsTr("Sending transaction ..."));
          currentWallet.commitTransactionAsync(transaction);
      }
      
      //交易广播后
      function onTransactionCommitted(success, transaction, txid) {
          hideProcessingSplash();
          if (!success) {
              console.log("Error committing transaction: " + transaction.errorString);
              informationPopup.title = qsTr("Error") + translationManager.emptyString
              informationPopup.text  = qsTr("Couldn't send the money: ") + transaction.errorString
              informationPopup.icon  = StandardIcon.Critical
          } else {
              var txid_text = ""
              informationPopup.title = qsTr("Information") + translationManager.emptyString
              for (var i = 0; i < txid.length; ++i) {
                  if (txid_text.length > 0)
                      txid_text += ", "
                  txid_text += txid[i]
              }
              informationPopup.text  = (viewOnly)? qsTr("Transaction saved to file: %1").arg(path) : qsTr("Monero sent successfully: %1 transaction(s) ").arg(txid.length) + txid_text + translationManager.emptyString
              informationPopup.icon  = StandardIcon.Information
              if (transactionDescription.length > 0) {
                  for (var i = 0; i < txid.length; ++i)
                    currentWallet.setUserNote(txid[i], transactionDescription);
              }
  
              // Clear tx fields
              middlePanel.transferView.clearFields()
  
          }
          informationPopup.onCloseCallback = null
          informationPopup.open()
          currentWallet.refresh()
          currentWallet.disposeTransaction(transaction)
          currentWallet.store();
      }
  ```

  

- `src/libwalletqt/Wallet.cpp`

  ```
  void Wallet::createTransactionAsync(const QString &dst_addr, const QString &payment_id,
                                 quint64 amount, quint32 mixin_count,
                                 PendingTransaction::Priority priority)
  {
      m_scheduler.run([this, dst_addr, payment_id, amount, mixin_count, priority] {
          PendingTransaction *tx = createTransaction(dst_addr, payment_id, amount, mixin_count, priority);
          
          //异步创建完成后,  发送信号 给QML, 对应QML中的 onTransactionCreated,
          //弹出对话框让用户确认
          emit transactionCreated(tx, dst_addr, payment_id, mixin_count);
      });
  }
  ```

- `monero/src/wallet/api/wallet.cpp`

  ```cpp
  
  PendingTransaction *WalletImpl::createTransaction(const string &dst_addr, const string &payment_id, optional<uint64_t> amount, uint32_t mixin_count,
                                                    PendingTransaction::Priority priority, uint32_t subaddr_account, std::set<uint32_t> subaddr_indices)
  
  {
      clearStatus();
      // Pause refresh thread while creating transaction
      pauseRefresh();
        
      cryptonote::address_parse_info info;
  
      // indicates if dst_addr is integrated address (address + payment_id)
      // TODO:  (https://bitcointalk.org/index.php?topic=753252.msg9985441#msg9985441)
      size_t fake_outs_count = mixin_count > 0 ? mixin_count : m_wallet->default_mixin();
      if (fake_outs_count == 0)
          fake_outs_count = DEFAULT_MIXIN;
      fake_outs_count = m_wallet->adjust_mixin(fake_outs_count);
  
      uint32_t adjusted_priority = m_wallet->adjust_priority(static_cast<uint32_t>(priority));
  
      PendingTransactionImpl * transaction = new PendingTransactionImpl(*this);
  
      do {
          if(!cryptonote::get_account_address_from_str(info, m_wallet->nettype(), dst_addr)) {
              // TODO: copy-paste 'if treating as an address fails, try as url' from simplewallet.cpp:1982
              setStatusError(tr("Invalid destination address"));
              break;
          }
  
  
          std::vector<uint8_t> extra;
          // if dst_addr is not an integrated address, parse payment_id
          if (!info.has_payment_id && !payment_id.empty()) {
              // copy-pasted from simplewallet.cpp:2212
              crypto::hash payment_id_long;
              bool r = tools::wallet2::parse_long_payment_id(payment_id, payment_id_long);
              if (r) {
                  std::string extra_nonce;
                  cryptonote::set_payment_id_to_tx_extra_nonce(extra_nonce, payment_id_long);
                  r = add_extra_nonce_to_tx_extra(extra, extra_nonce);
              } else {
                  r = tools::wallet2::parse_short_payment_id(payment_id, info.payment_id);
                  if (r) {
                      std::string extra_nonce;
                      set_encrypted_payment_id_to_tx_extra_nonce(extra_nonce, info.payment_id);
                      r = add_extra_nonce_to_tx_extra(extra, extra_nonce);
                  }
              }
  
              if (!r) {
                  setStatusError(tr("payment id has invalid format, expected 16 or 64 character hex string: ") + payment_id);
                  break;
              }
          }
          else if (info.has_payment_id) {
              std::string extra_nonce;
              set_encrypted_payment_id_to_tx_extra_nonce(extra_nonce, info.payment_id);
              bool r = add_extra_nonce_to_tx_extra(extra, extra_nonce);
              if (!r) {
                  setStatusError(tr("Failed to add short payment id: ") + epee::string_tools::pod_to_hex(info.payment_id));
                  break;
              }
          }
  
  
          //std::vector<tools::wallet2::pending_tx> ptx_vector;
  
          try {
              if (amount) {
                  vector<cryptonote::tx_destination_entry> dsts;
                  cryptonote::tx_destination_entry de;
                  de.original = dst_addr;
                  de.addr = info.address;
                  de.amount = *amount;
                  de.is_subaddress = info.is_subaddress;
                  de.is_integrated = info.has_payment_id;
                  dsts.push_back(de);
                  
                  //调用底层函数进行创建
                  transaction->m_pending_tx = m_wallet->create_transactions_2(dsts, fake_outs_count, 0 /* unlock_time */,
                                                                            adjusted_priority,
                                                                            extra, subaddr_account, subaddr_indices);
              } else {
                  // for the GUI, sweep_all (i.e. amount set as "(all)") will always sweep all the funds in all the addresses
                  if (subaddr_indices.empty())
                  {
                      for (uint32_t index = 0; index < m_wallet->get_num_subaddresses(subaddr_account); ++index)
                          subaddr_indices.insert(index);
                  }
                  transaction->m_pending_tx = m_wallet->create_transactions_all(0, info.address, info.is_subaddress, 1, fake_outs_count, 0 /* unlock_time */,
                                                                            adjusted_priority,
                                                                            extra, subaddr_account, subaddr_indices);
              }
  
              pendingTxPostProcess(transaction);
  
              if (multisig().isMultisig) {
                  auto tx_set = m_wallet->make_multisig_tx_set(transaction->m_pending_tx);
                  transaction->m_pending_tx = tx_set.m_ptx;
                  transaction->m_signers = tx_set.m_signers;
              }
          } catch (const tools::error::daemon_busy&) {
           //省略其他异常捕获...........
          } catch (...) {
              setStatusError(tr("unknown error"));
          }
      } while (false);
  
      statusWithErrorString(transaction->m_status, transaction->m_errorString);
      // Resume refresh thread
      startRefresh();
      return transaction;
  }
  ```
  
  

- wallet2.cpp

  ```cpp
  // Another implementation of transaction creation that is hopefully better
  // While there is anything left to pay, it goes through random outputs and tries
  // to fill the next destination/amount. If it fully fills it, it will use the
  // remainder to try to fill the next one as well.
  // The tx size if roughly estimated as a linear function of only inputs, and a
  // new tx will be created when that size goes above a given fraction of the
  // max tx size. At that point, more outputs may be added if the fee cannot be
  // satisfied.
  // If the next output in the next tx would go to the same destination (ie, we
  // cut off at a tx boundary in the middle of paying a given destination), the
  // fee will be carved out of the current input if possible, to avoid having to
  // add another output just for the fee and getting change.
  // This system allows for sending (almost) the entire balance, since it does
  // not generate spurious change in all txes, thus decreasing the instantaneous
  // usable balance.
  std::vector<wallet2::pending_tx> wallet2::create_transactions_2(std::vector<cryptonote::tx_destination_entry> dsts, const size_t fake_outs_count, const uint64_t unlock_time, uint32_t priority, const std::vector<uint8_t>& extra, uint32_t subaddr_account, std::set<uint32_t> subaddr_indices)
  {
    //ensure device is let in NONE mode in any case
    hw::device &hwdev = m_account.get_device();
    boost::unique_lock<hw::device> hwdev_lock (hwdev);
    hw::reset_mode rst(hwdev);  
  
    auto original_dsts = dsts;
  
    if(m_light_wallet) {
      // Populate m_transfers
      light_wallet_get_unspent_outs();
    }
    std::vector<std::pair<uint32_t, std::vector<size_t>>> unused_transfers_indices_per_subaddr;
    std::vector<std::pair<uint32_t, std::vector<size_t>>> unused_dust_indices_per_subaddr;
    uint64_t needed_money;
    uint64_t accumulated_fee, accumulated_outputs, accumulated_change;
    struct TX {
      std::vector<size_t> selected_transfers;
      std::vector<cryptonote::tx_destination_entry> dsts;
      cryptonote::transaction tx;
      pending_tx ptx;
      size_t weight;
      uint64_t needed_fee;
      std::vector<std::vector<tools::wallet2::get_outs_entry>> outs;
  
      TX() : weight(0), needed_fee(0) {}
  
      void add(const cryptonote::tx_destination_entry &de, uint64_t amount, unsigned int original_output_index, bool merge_destinations) {
        if (merge_destinations)
        {
          std::vector<cryptonote::tx_destination_entry>::iterator i;
          i = std::find_if(dsts.begin(), dsts.end(), [&](const cryptonote::tx_destination_entry &d) { return !memcmp (&d.addr, &de.addr, sizeof(de.addr)); });
          if (i == dsts.end())
          {
            dsts.push_back(de);
            i = dsts.end() - 1;
            i->amount = 0;
          }
          i->amount += amount;
        }
        else
        {
          THROW_WALLET_EXCEPTION_IF(original_output_index > dsts.size(), error::wallet_internal_error,
              std::string("original_output_index too large: ") + std::to_string(original_output_index) + " > " + std::to_string(dsts.size()));
          if (original_output_index == dsts.size())
          {
            dsts.push_back(de);
            dsts.back().amount = 0;
          }
          THROW_WALLET_EXCEPTION_IF(memcmp(&dsts[original_output_index].addr, &de.addr, sizeof(de.addr)), error::wallet_internal_error, "Mismatched destination address");
          dsts[original_output_index].amount += amount;
        }
      }
    };
    std::vector<TX> txes;
    bool adding_fee; // true if new outputs go towards fee, rather than destinations
    uint64_t needed_fee, available_for_fee = 0;
    uint64_t upper_transaction_weight_limit = get_upper_transaction_weight_limit();
    const bool use_per_byte_fee = use_fork_rules(HF_VERSION_PER_BYTE_FEE, 0);
    const bool use_rct = use_fork_rules(4, 0);
    const bool bulletproof = use_fork_rules(get_bulletproof_fork(), 0);
    const rct::RCTConfig rct_config {
      bulletproof ? rct::RangeProofPaddedBulletproof : rct::RangeProofBorromean,
      bulletproof ? (use_fork_rules(HF_VERSION_SMALLER_BP, -10) ? 2 : 1) : 0
    };
  
    const uint64_t base_fee  = get_base_fee();
    const uint64_t fee_multiplier = get_fee_multiplier(priority, get_fee_algorithm());
    const uint64_t fee_quantization_mask = get_fee_quantization_mask();
  
    // throw if attempting a transaction with no destinations
    THROW_WALLET_EXCEPTION_IF(dsts.empty(), error::zero_destination);
  
    // calculate total amount being sent to all destinations
    // throw if total amount overflows uint64_t
    needed_money = 0;
    for(auto& dt: dsts)
    {
      THROW_WALLET_EXCEPTION_IF(0 == dt.amount, error::zero_destination);
      needed_money += dt.amount;
      LOG_PRINT_L2("transfer: adding " << print_money(dt.amount) << ", for a total of " << print_money (needed_money));
      THROW_WALLET_EXCEPTION_IF(needed_money < dt.amount, error::tx_sum_overflow, dsts, 0, m_nettype);
    }
  
    // throw if attempting a transaction with no money
    THROW_WALLET_EXCEPTION_IF(needed_money == 0, error::zero_destination);
  
    std::map<uint32_t, std::pair<uint64_t, uint64_t>> unlocked_balance_per_subaddr = unlocked_balance_per_subaddress(subaddr_account);
    std::map<uint32_t, uint64_t> balance_per_subaddr = balance_per_subaddress(subaddr_account);
  
    if (subaddr_indices.empty()) // "index=<N1>[,<N2>,...]" wasn't specified -> use all the indices with non-zero unlocked balance
    {
      for (const auto& i : balance_per_subaddr)
        subaddr_indices.insert(i.first);
    }
  
    // early out if we know we can't make it anyway
    // we could also check for being within FEE_PER_KB, but if the fee calculation
    // ever changes, this might be missed, so let this go through
    const uint64_t min_fee = (fee_multiplier * base_fee * estimate_tx_size(use_rct, 1, fake_outs_count, 2, extra.size(), bulletproof));
    uint64_t balance_subtotal = 0;
    uint64_t unlocked_balance_subtotal = 0;
    for (uint32_t index_minor : subaddr_indices)
    {
      balance_subtotal += balance_per_subaddr[index_minor];
      unlocked_balance_subtotal += unlocked_balance_per_subaddr[index_minor].first;
    }
    THROW_WALLET_EXCEPTION_IF(needed_money + min_fee > balance_subtotal, error::not_enough_money,
      balance_subtotal, needed_money, 0);
    // first check overall balance is enough, then unlocked one, so we throw distinct exceptions
    THROW_WALLET_EXCEPTION_IF(needed_money + min_fee > unlocked_balance_subtotal, error::not_enough_unlocked_money,
        unlocked_balance_subtotal, needed_money, 0);
  
    for (uint32_t i : subaddr_indices)
      LOG_PRINT_L2("Candidate subaddress index for spending: " << i);
  
    // determine threshold for fractional amount
    const size_t tx_weight_one_ring = estimate_tx_weight(use_rct, 1, fake_outs_count, 2, 0, bulletproof);
    const size_t tx_weight_two_rings = estimate_tx_weight(use_rct, 2, fake_outs_count, 2, 0, bulletproof);
    THROW_WALLET_EXCEPTION_IF(tx_weight_one_ring > tx_weight_two_rings, error::wallet_internal_error, "Estimated tx weight with 1 input is larger than with 2 inputs!");
    const size_t tx_weight_per_ring = tx_weight_two_rings - tx_weight_one_ring;
    const uint64_t fractional_threshold = (fee_multiplier * base_fee * tx_weight_per_ring) / (use_per_byte_fee ? 1 : 1024);
  
    // gather all dust and non-dust outputs belonging to specified subaddresses
    size_t num_nondust_outputs = 0;
    size_t num_dust_outputs = 0;
    for (size_t i = 0; i < m_transfers.size(); ++i)
    {
      const transfer_details& td = m_transfers[i];
      if (m_ignore_fractional_outputs && td.amount() < fractional_threshold)
      {
        MDEBUG("Ignoring output " << i << " of amount " << print_money(td.amount()) << " which is below threshold " << print_money(fractional_threshold));
        continue;
      }
      if (!td.m_spent && !td.m_frozen && !td.m_key_image_partial && (use_rct ? true : !td.is_rct()) && is_transfer_unlocked(td) && td.m_subaddr_index.major == subaddr_account && subaddr_indices.count(td.m_subaddr_index.minor) == 1)
      {
        const uint32_t index_minor = td.m_subaddr_index.minor;
        auto find_predicate = [&index_minor](const std::pair<uint32_t, std::vector<size_t>>& x) { return x.first == index_minor; };
        if ((td.is_rct()) || is_valid_decomposed_amount(td.amount()))
        {
          auto found = std::find_if(unused_transfers_indices_per_subaddr.begin(), unused_transfers_indices_per_subaddr.end(), find_predicate);
          if (found == unused_transfers_indices_per_subaddr.end())
          {
            unused_transfers_indices_per_subaddr.push_back({index_minor, {i}});
          }
          else
          {
            found->second.push_back(i);
          }
          ++num_nondust_outputs;
        }
        else
        {
          auto found = std::find_if(unused_dust_indices_per_subaddr.begin(), unused_dust_indices_per_subaddr.end(), find_predicate);
          if (found == unused_dust_indices_per_subaddr.end())
          {
            unused_dust_indices_per_subaddr.push_back({index_minor, {i}});
          }
          else
          {
            found->second.push_back(i);
          }
          ++num_dust_outputs;
        }
      }
    }
  
    // sort output indices
    {
      auto sort_predicate = [&unlocked_balance_per_subaddr] (const std::pair<uint32_t, std::vector<size_t>>& x, const std::pair<uint32_t, std::vector<size_t>>& y)
      {
        return unlocked_balance_per_subaddr[x.first].first > unlocked_balance_per_subaddr[y.first].first;
      };
      std::sort(unused_transfers_indices_per_subaddr.begin(), unused_transfers_indices_per_subaddr.end(), sort_predicate);
      std::sort(unused_dust_indices_per_subaddr.begin(), unused_dust_indices_per_subaddr.end(), sort_predicate);
    }
  
    LOG_PRINT_L2("Starting with " << num_nondust_outputs << " non-dust outputs and " << num_dust_outputs << " dust outputs");
  
    if (unused_dust_indices_per_subaddr.empty() && unused_transfers_indices_per_subaddr.empty())
      return std::vector<wallet2::pending_tx>();
  
    // if empty, put dummy entry so that the front can be referenced later in the loop
    if (unused_dust_indices_per_subaddr.empty())
      unused_dust_indices_per_subaddr.push_back({});
    if (unused_transfers_indices_per_subaddr.empty())
      unused_transfers_indices_per_subaddr.push_back({});
  
    // start with an empty tx
    txes.push_back(TX());
    accumulated_fee = 0;
    accumulated_outputs = 0;
    accumulated_change = 0;
    adding_fee = false;
    needed_fee = 0;
    std::vector<std::vector<tools::wallet2::get_outs_entry>> outs;
  
    // for rct, since we don't see the amounts, we will try to make all transactions
    // look the same, with 1 or 2 inputs, and 2 outputs. One input is preferable, as
    // this prevents linking to another by provenance analysis, but two is ok if we
    // try to pick outputs not from the same block. We will get two outputs, one for
    // the destination, and one for change.
    LOG_PRINT_L2("checking preferred");
    std::vector<size_t> preferred_inputs;
    uint64_t rct_outs_needed = 2 * (fake_outs_count + 1);
    rct_outs_needed += 100; // some fudge factor since we don't know how many are locked
    if (use_rct)
    {
      // this is used to build a tx that's 1 or 2 inputs, and 2 outputs, which
      // will get us a known fee.
      uint64_t estimated_fee = estimate_fee(use_per_byte_fee, use_rct, 2, fake_outs_count, 2, extra.size(), bulletproof, base_fee, fee_multiplier, fee_quantization_mask);
      preferred_inputs = pick_preferred_rct_inputs(needed_money + estimated_fee, subaddr_account, subaddr_indices);
      if (!preferred_inputs.empty())
      {
        string s;
        for (auto i: preferred_inputs) s += boost::lexical_cast<std::string>(i) + " (" + print_money(m_transfers[i].amount()) + ") ";
        LOG_PRINT_L1("Found preferred rct inputs for rct tx: " << s);
  
        // bring the list of available outputs stored by the same subaddress index to the front of the list
        uint32_t index_minor = m_transfers[preferred_inputs[0]].m_subaddr_index.minor;
        for (size_t i = 1; i < unused_transfers_indices_per_subaddr.size(); ++i)
        {
          if (unused_transfers_indices_per_subaddr[i].first == index_minor)
          {
            std::swap(unused_transfers_indices_per_subaddr[0], unused_transfers_indices_per_subaddr[i]);
            break;
          }
        }
        for (size_t i = 1; i < unused_dust_indices_per_subaddr.size(); ++i)
        {
          if (unused_dust_indices_per_subaddr[i].first == index_minor)
          {
            std::swap(unused_dust_indices_per_subaddr[0], unused_dust_indices_per_subaddr[i]);
            break;
          }
        }
      }
    }
    LOG_PRINT_L2("done checking preferred");
  
    // while:
    // - we have something to send
    // - or we need to gather more fee
    // - or we have just one input in that tx, which is rct (to try and make all/most rct txes 2/2)
    unsigned int original_output_index = 0;
    std::vector<size_t>* unused_transfers_indices = &unused_transfers_indices_per_subaddr[0].second;
    std::vector<size_t>* unused_dust_indices      = &unused_dust_indices_per_subaddr[0].second;
    
    hwdev.set_mode(hw::device::TRANSACTION_CREATE_FAKE);
    while ((!dsts.empty() && dsts[0].amount > 0) || adding_fee || !preferred_inputs.empty() || should_pick_a_second_output(use_rct, txes.back().selected_transfers.size(), *unused_transfers_indices, *unused_dust_indices)) {
      TX &tx = txes.back();
  
      LOG_PRINT_L2("Start of loop with " << unused_transfers_indices->size() << " " << unused_dust_indices->size() << ", tx.dsts.size() " << tx.dsts.size());
      LOG_PRINT_L2("unused_transfers_indices: " << strjoin(*unused_transfers_indices, " "));
      LOG_PRINT_L2("unused_dust_indices: " << strjoin(*unused_dust_indices, " "));
      LOG_PRINT_L2("dsts size " << dsts.size() << ", first " << (dsts.empty() ? "-" : cryptonote::print_money(dsts[0].amount)));
      LOG_PRINT_L2("adding_fee " << adding_fee << ", use_rct " << use_rct);
  
      // if we need to spend money and don't have any left, we fail
      if (unused_dust_indices->empty() && unused_transfers_indices->empty()) {
        LOG_PRINT_L2("No more outputs to choose from");
        THROW_WALLET_EXCEPTION_IF(1, error::tx_not_possible, unlocked_balance(subaddr_account), needed_money, accumulated_fee + needed_fee);
      }
  
      // get a random unspent output and use it to pay part (or all) of the current destination (and maybe next one, etc)
      // This could be more clever, but maybe at the cost of making probabilistic inferences easier
      size_t idx;
      if (!preferred_inputs.empty()) {
        idx = pop_back(preferred_inputs);
        pop_if_present(*unused_transfers_indices, idx);
        pop_if_present(*unused_dust_indices, idx);
      } else if ((dsts.empty() || dsts[0].amount == 0) && !adding_fee) {
        // the "make rct txes 2/2" case - we pick a small value output to "clean up" the wallet too
        std::vector<size_t> indices = get_only_rct(*unused_dust_indices, *unused_transfers_indices);
        idx = pop_best_value(indices, tx.selected_transfers, true);
  
        // we might not want to add it if it's a large output and we don't have many left
        if (m_transfers[idx].amount() >= m_min_output_value) {
          if (get_count_above(m_transfers, *unused_transfers_indices, m_min_output_value) < m_min_output_count) {
            LOG_PRINT_L2("Second output was not strictly needed, and we're running out of outputs above " << print_money(m_min_output_value) << ", not adding");
            break;
          }
        }
  
        // since we're trying to add a second output which is not strictly needed,
        // we only add it if it's unrelated enough to the first one
        float relatedness = get_output_relatedness(m_transfers[idx], m_transfers[tx.selected_transfers.front()]);
        if (relatedness > SECOND_OUTPUT_RELATEDNESS_THRESHOLD)
        {
          LOG_PRINT_L2("Second output was not strictly needed, and relatedness " << relatedness << ", not adding");
          break;
        }
        pop_if_present(*unused_transfers_indices, idx);
        pop_if_present(*unused_dust_indices, idx);
      } else
        idx = pop_best_value(unused_transfers_indices->empty() ? *unused_dust_indices : *unused_transfers_indices, tx.selected_transfers);
  
      const transfer_details &td = m_transfers[idx];
      LOG_PRINT_L2("Picking output " << idx << ", amount " << print_money(td.amount()) << ", ki " << td.m_key_image);
  
      // add this output to the list to spend
      tx.selected_transfers.push_back(idx);
      uint64_t available_amount = td.amount();
      accumulated_outputs += available_amount;
  
      // clear any fake outs we'd already gathered, since we'll need a new set
      outs.clear();
  
      if (adding_fee)
      {
        LOG_PRINT_L2("We need more fee, adding it to fee");
        available_for_fee += available_amount;
      }
      else
      {
        while (!dsts.empty() && dsts[0].amount <= available_amount && estimate_tx_weight(use_rct, tx.selected_transfers.size(), fake_outs_count, tx.dsts.size()+1, extra.size(), bulletproof) < TX_WEIGHT_TARGET(upper_transaction_weight_limit))
        {
          // we can fully pay that destination
          LOG_PRINT_L2("We can fully pay " << get_account_address_as_str(m_nettype, dsts[0].is_subaddress, dsts[0].addr) <<
            " for " << print_money(dsts[0].amount));
          tx.add(dsts[0], dsts[0].amount, original_output_index, m_merge_destinations);
          available_amount -= dsts[0].amount;
          dsts[0].amount = 0;
          pop_index(dsts, 0);
          ++original_output_index;
        }
  
        if (available_amount > 0 && !dsts.empty() && estimate_tx_weight(use_rct, tx.selected_transfers.size(), fake_outs_count, tx.dsts.size()+1, extra.size(), bulletproof) < TX_WEIGHT_TARGET(upper_transaction_weight_limit)) {
          // we can partially fill that destination
          LOG_PRINT_L2("We can partially pay " << get_account_address_as_str(m_nettype, dsts[0].is_subaddress, dsts[0].addr) <<
            " for " << print_money(available_amount) << "/" << print_money(dsts[0].amount));
          tx.add(dsts[0], available_amount, original_output_index, m_merge_destinations);
          dsts[0].amount -= available_amount;
          available_amount = 0;
        }
      }
  
      // here, check if we need to sent tx and start a new one
      LOG_PRINT_L2("Considering whether to create a tx now, " << tx.selected_transfers.size() << " inputs, tx limit "
        << upper_transaction_weight_limit);
      bool try_tx = false;
      // if we have preferred picks, but haven't yet used all of them, continue
      if (preferred_inputs.empty())
      {
        if (adding_fee)
        {
          /* might not actually be enough if adding this output bumps size to next kB, but we need to try */
          try_tx = available_for_fee >= needed_fee;
        }
        else
        {
          const size_t estimated_rct_tx_weight = estimate_tx_weight(use_rct, tx.selected_transfers.size(), fake_outs_count, tx.dsts.size()+1, extra.size(), bulletproof);
          try_tx = dsts.empty() || (estimated_rct_tx_weight >= TX_WEIGHT_TARGET(upper_transaction_weight_limit));
          THROW_WALLET_EXCEPTION_IF(try_tx && tx.dsts.empty(), error::tx_too_big, estimated_rct_tx_weight, upper_transaction_weight_limit);
        }
      }
  
      if (try_tx) {
        cryptonote::transaction test_tx;
        pending_tx test_ptx;
  
        needed_fee = estimate_fee(use_per_byte_fee, use_rct ,tx.selected_transfers.size(), fake_outs_count, tx.dsts.size()+1, extra.size(), bulletproof, base_fee, fee_multiplier, fee_quantization_mask);
  
        uint64_t inputs = 0, outputs = needed_fee;
        for (size_t idx: tx.selected_transfers) inputs += m_transfers[idx].amount();
        for (const auto &o: tx.dsts) outputs += o.amount;
  
        if (inputs < outputs)
        {
          LOG_PRINT_L2("We don't have enough for the basic fee, switching to adding_fee");
          adding_fee = true;
          goto skip_tx;
        }
  
        LOG_PRINT_L2("Trying to create a tx now, with " << tx.dsts.size() << " outputs and " <<
          tx.selected_transfers.size() << " inputs");
        if (use_rct)
          transfer_selected_rct(tx.dsts, tx.selected_transfers, fake_outs_count, outs, unlock_time, needed_fee, extra,
            test_tx, test_ptx, rct_config);
        else
          transfer_selected(tx.dsts, tx.selected_transfers, fake_outs_count, outs, unlock_time, needed_fee, extra,
            detail::digit_split_strategy, tx_dust_policy(::config::DEFAULT_DUST_THRESHOLD), test_tx, test_ptx);
        auto txBlob = t_serializable_object_to_blob(test_ptx.tx);
        needed_fee = calculate_fee(use_per_byte_fee, test_ptx.tx, txBlob.size(), base_fee, fee_multiplier, fee_quantization_mask);
        available_for_fee = test_ptx.fee + test_ptx.change_dts.amount + (!test_ptx.dust_added_to_fee ? test_ptx.dust : 0);
        LOG_PRINT_L2("Made a " << get_weight_string(test_ptx.tx, txBlob.size()) << " tx, with " << print_money(available_for_fee) << " available for fee (" <<
          print_money(needed_fee) << " needed)");
  
        if (needed_fee > available_for_fee && !dsts.empty() && dsts[0].amount > 0)
        {
          // we don't have enough for the fee, but we've only partially paid the current address,
          // so we can take the fee from the paid amount, since we'll have to make another tx anyway
          std::vector<cryptonote::tx_destination_entry>::iterator i;
          i = std::find_if(tx.dsts.begin(), tx.dsts.end(),
            [&](const cryptonote::tx_destination_entry &d) { return !memcmp (&d.addr, &dsts[0].addr, sizeof(dsts[0].addr)); });
          THROW_WALLET_EXCEPTION_IF(i == tx.dsts.end(), error::wallet_internal_error, "paid address not found in outputs");
          if (i->amount > needed_fee)
          {
            uint64_t new_paid_amount = i->amount /*+ test_ptx.fee*/ - needed_fee;
            LOG_PRINT_L2("Adjusting amount paid to " << get_account_address_as_str(m_nettype, i->is_subaddress, i->addr) << " from " <<
              print_money(i->amount) << " to " << print_money(new_paid_amount) << " to accommodate " <<
              print_money(needed_fee) << " fee");
            dsts[0].amount += i->amount - new_paid_amount;
            i->amount = new_paid_amount;
            test_ptx.fee = needed_fee;
            available_for_fee = needed_fee;
          }
        }
  
        if (needed_fee > available_for_fee)
        {
          LOG_PRINT_L2("We could not make a tx, switching to fee accumulation");
  
          adding_fee = true;
        }
        else
        {
          LOG_PRINT_L2("We made a tx, adjusting fee and saving it, we need " << print_money(needed_fee) << " and we have " << print_money(test_ptx.fee));
          while (needed_fee > test_ptx.fee) {
            if (use_rct)
              transfer_selected_rct(tx.dsts, tx.selected_transfers, fake_outs_count, outs, unlock_time, needed_fee, extra,
                test_tx, test_ptx, rct_config);
            else
              transfer_selected(tx.dsts, tx.selected_transfers, fake_outs_count, outs, unlock_time, needed_fee, extra,
                detail::digit_split_strategy, tx_dust_policy(::config::DEFAULT_DUST_THRESHOLD), test_tx, test_ptx);
            txBlob = t_serializable_object_to_blob(test_ptx.tx);
            needed_fee = calculate_fee(use_per_byte_fee, test_ptx.tx, txBlob.size(), base_fee, fee_multiplier, fee_quantization_mask);
            LOG_PRINT_L2("Made an attempt at a  final " << get_weight_string(test_ptx.tx, txBlob.size()) << " tx, with " << print_money(test_ptx.fee) <<
              " fee  and " << print_money(test_ptx.change_dts.amount) << " change");
          }
  
          LOG_PRINT_L2("Made a final " << get_weight_string(test_ptx.tx, txBlob.size()) << " tx, with " << print_money(test_ptx.fee) <<
            " fee  and " << print_money(test_ptx.change_dts.amount) << " change");
  
          tx.tx = test_tx;
          tx.ptx = test_ptx;
          tx.weight = get_transaction_weight(test_tx, txBlob.size());
          tx.outs = outs;
          tx.needed_fee = test_ptx.fee;
          accumulated_fee += test_ptx.fee;
          accumulated_change += test_ptx.change_dts.amount;
          adding_fee = false;
          if (!dsts.empty())
          {
            LOG_PRINT_L2("We have more to pay, starting another tx");
            txes.push_back(TX());
            original_output_index = 0;
          }
        }
      }
  
  skip_tx:
      // if unused_*_indices is empty while unused_*_indices_per_subaddr has multiple elements, and if we still have something to pay, 
      // pop front of unused_*_indices_per_subaddr and have unused_*_indices point to the front of unused_*_indices_per_subaddr
      if ((!dsts.empty() && dsts[0].amount > 0) || adding_fee)
      {
        if (unused_transfers_indices->empty() && unused_transfers_indices_per_subaddr.size() > 1)
        {
          unused_transfers_indices_per_subaddr.erase(unused_transfers_indices_per_subaddr.begin());
          unused_transfers_indices = &unused_transfers_indices_per_subaddr[0].second;
        }
        if (unused_dust_indices->empty() && unused_dust_indices_per_subaddr.size() > 1)
        {
          unused_dust_indices_per_subaddr.erase(unused_dust_indices_per_subaddr.begin());
          unused_dust_indices = &unused_dust_indices_per_subaddr[0].second;
        }
      }
    }
  
    if (adding_fee)
    {
      LOG_PRINT_L1("We ran out of outputs while trying to gather final fee");
      THROW_WALLET_EXCEPTION_IF(1, error::tx_not_possible, unlocked_balance(subaddr_account), needed_money, accumulated_fee + needed_fee);
    }
  
    LOG_PRINT_L1("Done creating " << txes.size() << " transactions, " << print_money(accumulated_fee) <<
      " total fee, " << print_money(accumulated_change) << " total change");
  
    hwdev.set_mode(hw::device::TRANSACTION_CREATE_REAL);
    for (std::vector<TX>::iterator i = txes.begin(); i != txes.end(); ++i)
    {
      TX &tx = *i;
      cryptonote::transaction test_tx;
      pending_tx test_ptx;
      if (use_rct) {
        transfer_selected_rct(tx.dsts,                    /* NOMOD std::vector<cryptonote::tx_destination_entry> dsts,*/
                              tx.selected_transfers,      /* const std::list<size_t> selected_transfers */
                              fake_outs_count,            /* CONST size_t fake_outputs_count, */
                              tx.outs,                    /* MOD   std::vector<std::vector<tools::wallet2::get_outs_entry>> &outs, */
                              unlock_time,                /* CONST uint64_t unlock_time,  */
                              tx.needed_fee,              /* CONST uint64_t fee, */
                              extra,                      /* const std::vector<uint8_t>& extra, */
                              test_tx,                    /* OUT   cryptonote::transaction& tx, */
                              test_ptx,                   /* OUT   cryptonote::transaction& tx, */
                              rct_config);
      } else {
        transfer_selected(tx.dsts,
                          tx.selected_transfers,
                          fake_outs_count,
                          tx.outs,
                          unlock_time,
                          tx.needed_fee,
                          extra,
                          detail::digit_split_strategy,
                          tx_dust_policy(::config::DEFAULT_DUST_THRESHOLD),
                          test_tx,
                          test_ptx);
      }
      auto txBlob = t_serializable_object_to_blob(test_ptx.tx);
      tx.tx = test_tx;
      tx.ptx = test_ptx;
      tx.weight = get_transaction_weight(test_tx, txBlob.size());
    }
  
    std::vector<wallet2::pending_tx> ptx_vector;
    for (std::vector<TX>::iterator i = txes.begin(); i != txes.end(); ++i)
    {
      TX &tx = *i;
      uint64_t tx_money = 0;
      for (size_t idx: tx.selected_transfers)
        tx_money += m_transfers[idx].amount();
      LOG_PRINT_L1("  Transaction " << (1+std::distance(txes.begin(), i)) << "/" << txes.size() <<
        " " << get_transaction_hash(tx.ptx.tx) << ": " << get_weight_string(tx.weight) << ", sending " << print_money(tx_money) << " in " << tx.selected_transfers.size() <<
        " outputs to " << tx.dsts.size() << " destination(s), including " <<
        print_money(tx.ptx.fee) << " fee, " << print_money(tx.ptx.change_dts.amount) << " change");
      ptx_vector.push_back(tx.ptx);
    }
  
    THROW_WALLET_EXCEPTION_IF(!sanity_check(ptx_vector, original_dsts), error::wallet_internal_error, "Created transaction(s) failed sanity check");
  
    // if we made it this far, we're OK to actually send the transactions
    return ptx_vector;
  }
  
  ```

  

